from fastapi import APIRouter, HTTPException, Response, status

from ..desk_tracking import (
    DeskStatus,
    DeskTracker,
    HeightReading,
    NamedTimerProfile,
    SittingPeriod,
    TimerProfile,
    TimerProfileInput,
    TimerProfileRegistry,
)

router = APIRouter(prefix="/desk", tags=["desk"])
tracker = DeskTracker()
profile_registry = TimerProfileRegistry(tracker.profile)


@router.get("/profile", response_model=TimerProfile)
async def read_profile() -> TimerProfile:
    return tracker.profile


@router.put("/profile", response_model=TimerProfile)
async def update_profile(profile: TimerProfile) -> TimerProfile:
    tracker.update_profile(profile)
    active = profile_registry.get_profile(profile_registry.active_profile_id)
    if active is not None:
        profile_registry.update_profile(
            active.profile_id,
            TimerProfileInput(name=active.name, settings=profile),
        )
    return tracker.profile


@router.get("/profiles", response_model=list[NamedTimerProfile])
async def list_profiles() -> list[NamedTimerProfile]:
    return profile_registry.list_profiles()


@router.post(
    "/profiles",
    response_model=NamedTimerProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(profile: TimerProfileInput) -> NamedTimerProfile:
    return profile_registry.create_profile(profile)


@router.put("/profiles/{profile_id}", response_model=NamedTimerProfile)
async def update_named_profile(
    profile_id: str,
    profile: TimerProfileInput,
) -> NamedTimerProfile:
    saved = profile_registry.update_profile(profile_id, profile)
    if saved is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile_id == profile_registry.active_profile_id:
        tracker.update_profile(saved.settings)
    return saved


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str) -> Response:
    if profile_registry.get_profile(profile_id) is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not profile_registry.delete_profile(profile_id):
        raise HTTPException(status_code=409, detail="Cannot delete the default or active profile")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/profiles/{profile_id}/activate", response_model=NamedTimerProfile)
async def activate_profile(profile_id: str) -> NamedTimerProfile:
    profile = profile_registry.activate_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    tracker.update_profile(profile.settings)
    return profile


@router.post("/readings", response_model=DeskStatus)
async def record_reading(reading: HeightReading) -> DeskStatus:
    if tracker.last_reading_at is not None and reading.recorded_at < tracker.last_reading_at:
        raise HTTPException(status_code=422, detail="recorded_at cannot precede the previous reading")
    return tracker.record(reading)


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
