from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.desk_tracking import (
    DeskPosition,
    DeskTracker,
    HeightReading,
    TimerProfile,
)


def test_tracker_status_handles_no_readings():
    tracker = DeskTracker()

    status = tracker.status()

    assert status.height_cm is None
    assert status.position is None
    assert status.sitting_seconds == 0
    assert status.standing_seconds == 0
    assert status.position_seconds == 0
    assert status.target_seconds is None
    assert status.timer_overdue is False
    assert status.last_reading_at is None
    assert tracker.measurements.list() == []
    assert tracker.measurements.latest() is None
    assert tracker.sitting_periods.list() == []


def test_reading_defaults_and_normalizes_timestamp_to_utc():
    reading = HeightReading(height_cm=70)
    naive_reading = HeightReading(
        height_cm=70,
        recorded_at=datetime(2026, 10, 28, 12, 0),
    )

    assert reading.recorded_at.tzinfo == timezone.utc
    assert naive_reading.recorded_at.tzinfo == timezone.utc


@pytest.mark.parametrize(
    "profile_data",
    [
        {"seated_max_height_cm": 100, "standing_min_height_cm": 100},
        {"seated_max_height_cm": 101, "standing_min_height_cm": 100},
        {"sitting_target_minutes": 0},
        {"position_confirmation_seconds": 301},
        {"unexpected_setting": True},
    ],
)
def test_profile_rejects_invalid_or_unknown_configuration(profile_data):
    with pytest.raises(ValidationError):
        TimerProfile(**profile_data)


def test_profile_uses_defaults_for_omitted_configuration():
    profile = TimerProfile(sitting_target_minutes=20)

    assert profile.seated_max_height_cm == 75
    assert profile.standing_min_height_cm == 95
    assert profile.sitting_target_minutes == 20
    assert profile.standing_target_minutes == 10
    assert profile.position_confirmation_seconds == 5


@pytest.mark.parametrize("height_cm", [0, -1, 200.1])
def test_reading_rejects_missing_or_out_of_range_height(height_cm):
    with pytest.raises(ValidationError):
        HeightReading(height_cm=height_cm)


def test_reading_requires_height():
    with pytest.raises(ValidationError, match="height_cm"):
        HeightReading()

