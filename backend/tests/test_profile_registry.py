from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app import backend_app
from app.desk_tracking import DeskTracker, HeightReading, TimerProfile, TimerProfileInput, TimerProfileRegistry


def make_profile(name: str, sitting_minutes: int = 30) -> TimerProfileInput:
    return TimerProfileInput(
        name=name,
        settings=TimerProfile(sitting_target_minutes=sitting_minutes),
    )


def test_registry_starts_with_default_profile():
    registry = TimerProfileRegistry()

    profiles = registry.list_profiles()

    assert len(profiles) == 1
    assert profiles[0].profile_id == "default"
    assert registry.active_profile_id == "default"


def test_create_update_and_activate_named_profile():
    registry = TimerProfileRegistry()
    created = registry.create_profile(make_profile("Work", sitting_minutes=25))

    updated = registry.update_profile(created.profile_id, make_profile("Focus", 20))
    activated = registry.activate_profile(created.profile_id)

    assert updated is not None
    assert updated.name == "Focus"
    assert updated.settings.sitting_target_minutes == 20
    assert activated == updated
    assert registry.active_profile_id == created.profile_id


def test_registry_prevents_deleting_default_or_active_profile():
    registry = TimerProfileRegistry()
    created = registry.create_profile(make_profile("Work"))

    assert registry.delete_profile("default") is False
    assert registry.delete_profile(created.profile_id) is True
    assert registry.delete_profile("missing") is False


def test_tracker_requires_threshold_confirmation_before_switching_position():
    profile = TimerProfile(seated_max_height_cm=70, standing_min_height_cm=100, position_confirmation_seconds=10)
    tracker = DeskTracker(profile)
    start = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    tracker.record(HeightReading(height_cm=60, recorded_at=start))
    tracker.record(HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=2)))
    status = tracker.record(HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=12)))

    assert status.position == "standing"
    assert len(tracker.measurements.list()) == 3


def test_desk_api_profile_and_readings_endpoints_work():
    client = TestClient(backend_app)

    profile_response = client.put(
        "/desk/profile?token=jessica",
        json={
            "seated_max_height_cm": 70,
            "standing_min_height_cm": 100,
            "sitting_target_minutes": 2,
            "standing_target_minutes": 5,
            "position_confirmation_seconds": 0,
        },
    )
    reading_response = client.post(
        "/desk/readings?token=jessica",
        json={"height_cm": 65, "recorded_at": "2026-10-28T12:00:00+00:00"},
    )
    status_response = client.get("/desk/status?token=jessica")
    history_response = client.get("/desk/measurements?token=jessica")

    assert profile_response.status_code == 200
    assert profile_response.json()["sitting_target_minutes"] == 2
    assert reading_response.status_code == 200
    assert reading_response.json()["position"] == "sitting"
    assert status_response.status_code == 200
    assert status_response.json()["target_seconds"] == 120
    assert history_response.status_code == 200
    assert len(history_response.json()) >= 1
