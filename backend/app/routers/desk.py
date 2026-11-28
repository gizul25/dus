from threading import RLock
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status, Request

from .. import desk_reminder
from ..desk_tracking import (
    DeskStatus,
    DeskTracker,
    HeightReading,
    NamedTimerProfile,
    SittingPeriod,
    TimerProfile,
    TimerProfileInput,
    TimerProfileRegistry,
    DeskPosition
)

from ..desk_reminder import (
    get_saved_preferences,
    reminder_functionality,
    is_forced_standup_reminder,
    check_height
)

from ..desk_reminder import enable_reminder

router = APIRouter(prefix="/desk", tags=["desk"])
tracker = DeskTracker()
profile_registry = TimerProfileRegistry(tracker.profile)
tracker_sequence = 0
state_lock = RLock()


def _save_state(db: Any) -> None:
    db["desk_state"].replace_one(
        {"_id": "active"},
        {
            "_id": "active",
            "tracker": tracker.snapshot(),
            "profiles": profile_registry.snapshot(),
            "last_sequence": tracker_sequence,
            "ordinary_reminder_active": desk_reminder.ordinary_reminder_active,
            "forced_standup_active": desk_reminder.forced_standup_active,
        },
        upsert=True,
    )


def _persist_closed_periods(db: Any, sequence: int, previous_count: int) -> None:
    new_periods = tracker.sitting_periods.list()[previous_count:]
    for period in new_periods:
        db["desk_sitting_periods"].replace_one(
            {"_id": sequence},
            {
                "_id": sequence,
                "sequence": sequence,
                **period.model_dump(),
            },
            upsert=True,
        )


def restore_desk_state(db: Any) -> None:
    global tracker, profile_registry, tracker_sequence

    db["desk_measurements"].create_index("sequence", unique=True)
    db["desk_sitting_periods"].create_index("sequence", unique=True)
    saved = db["desk_state"].find_one({"_id": "active"}) or {}

    tracker = DeskTracker()
    if "tracker" in saved:
        tracker.restore_snapshot(saved["tracker"])

    profile_registry = TimerProfileRegistry(tracker.profile)
    if "profiles" in saved:
        profile_registry.restore_snapshot(saved["profiles"])

    desk_reminder.ordinary_reminder_active = bool(
        saved.get("ordinary_reminder_active", False)
    )
    desk_reminder.forced_standup_active = bool(
        saved.get("forced_standup_active", False)
    )

    tracker_sequence = int(saved.get("last_sequence", 0))
    for period in db["desk_sitting_periods"].find(
        {"sequence": {"$lte": tracker_sequence}}
    ).sort("sequence", 1):
        tracker.sitting_periods.add(SittingPeriod.model_validate(period))

    for measurement in db["desk_measurements"].find().sort("sequence", 1):
        sequence = int(measurement["sequence"])
        reading = HeightReading.model_validate(
            {
                "height_cm": measurement["height_cm"],
                "recorded_at": measurement["recorded_at"],
            }
        )
        if sequence <= tracker_sequence:
            tracker.measurements.add(reading)
            continue

        previous_period_count = len(tracker.sitting_periods.list())
        tracker.record(reading)
        tracker_sequence = sequence
        _persist_closed_periods(db, sequence, previous_period_count)

    if tracker_sequence != saved.get("last_sequence", 0):
        _save_state(db)


@router.get("/profile", response_model=TimerProfile)
async def read_profile() -> TimerProfile:
    return tracker.profile


@router.put("/profile", response_model=TimerProfile)
async def update_profile(profile: TimerProfile, request: Request) -> TimerProfile:
    with state_lock:
        tracker.update_profile(profile)
        active = profile_registry.get_profile(profile_registry.active_profile_id)
        if active is not None:
            profile_registry.update_profile(
                active.profile_id,
                TimerProfileInput(name=active.name, settings=profile),
            )
        _save_state(request.app.db)
    return tracker.profile


@router.get("/profiles", response_model=list[NamedTimerProfile])
async def list_profiles() -> list[NamedTimerProfile]:
    return profile_registry.list_profiles()


@router.post(
    "/profiles",
    response_model=NamedTimerProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    profile: TimerProfileInput,
    request: Request,
) -> NamedTimerProfile:
    with state_lock:
        saved = profile_registry.create_profile(profile)
        _save_state(request.app.db)
    return saved


@router.put("/profiles/{profile_id}", response_model=NamedTimerProfile)
async def update_named_profile(
    profile_id: str,
    profile: TimerProfileInput,
    request: Request,
) -> NamedTimerProfile:
    with state_lock:
        saved = profile_registry.update_profile(profile_id, profile)
        if saved is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile_id == profile_registry.active_profile_id:
            tracker.update_profile(saved.settings)
        _save_state(request.app.db)
    return saved


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str, request: Request) -> Response:
    with state_lock:
        if profile_registry.get_profile(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        if not profile_registry.delete_profile(profile_id):
            raise HTTPException(status_code=409, detail="Cannot delete the default or active profile")
        _save_state(request.app.db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/profiles/{profile_id}/activate", response_model=NamedTimerProfile)
async def activate_profile(profile_id: str, request: Request) -> NamedTimerProfile:
    with state_lock:
        profile = profile_registry.activate_profile(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        tracker.update_profile(profile.settings)
        _save_state(request.app.db)
    return profile


@router.post("/readings", response_model=DeskStatus)
def record_reading(reading: HeightReading, request: Request) -> DeskStatus:
    global tracker_sequence

    with state_lock:
        if tracker.last_reading_at is not None and reading.recorded_at < tracker.last_reading_at:
            raise HTTPException(status_code=422, detail="recorded_at cannot precede the previous reading")

        sequence = tracker_sequence + 1
        request.app.db["desk_measurements"].insert_one(
            {"sequence": sequence, **reading.model_dump()}
        )
        previous_period_count = len(tracker.sitting_periods.list())
        try:
            desk_status = tracker.record(reading)
        except ValueError:
            request.app.db["desk_measurements"].delete_one({"sequence": sequence})
            raise

        tracker_sequence = sequence
        if desk_status.reminder_due:
            preferences = get_saved_preferences(request)
            enabled_reminder = reminder_functionality(preferences)
            enable_reminder(enabled_reminder)
            is_forced_standup_reminder(preferences)
            tracker.reminder_triggered = True
        position = desk_status.position
        if DeskPosition.STANDING == position:
            check_height(desk_status.height_cm, tracker.profile.standing_min_height_cm)
        _persist_closed_periods(request.app.db, sequence, previous_period_count)
        _save_state(request.app.db)
        return desk_status


@router.get("/measurements", response_model=list[HeightReading])
async def read_measurements(limit: int | None = None) -> list[HeightReading]:
    items = tracker.measurements.list(limit)
    return items


@router.get("/sitting-periods", response_model=list[SittingPeriod])
async def read_sitting_periods(limit: int | None = None) -> list[SittingPeriod]:
    return tracker.sitting_periods.list(limit)


@router.get("/status", response_model=DeskStatus)
async def read_status() -> DeskStatus:
    return tracker.status()
