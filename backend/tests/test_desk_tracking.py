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


def test_unclassified_height_keeps_position_unknown_but_records_measurement():
    tracker = DeskTracker(
        TimerProfile(seated_max_height_cm=70, standing_min_height_cm=100)
    )
    recorded_at = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    status = tracker.record(HeightReading(height_cm=85, recorded_at=recorded_at))

    assert status.height_cm == 85
    assert status.position is None
    assert status.target_seconds is None
    assert status.last_reading_at == recorded_at
    assert tracker.measurements.latest().height_cm == 85
    assert tracker.sitting_periods.list() == []


def test_position_change_accumulates_elapsed_time_and_resets_position_timer():
    tracker = DeskTracker(
        TimerProfile(
            seated_max_height_cm=70,
            standing_min_height_cm=100,
            position_confirmation_seconds=5,
        )
    )
    start = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    tracker.record(HeightReading(height_cm=65, recorded_at=start))
    sitting_status = tracker.record(
        HeightReading(height_cm=65, recorded_at=start + timedelta(seconds=30))
    )
    tracker.record(
        HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=32))
    )
    standing_status = tracker.record(
        HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=37))
    )
    continued_standing_status = tracker.record(
        HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=47))
    )

    assert sitting_status.position == DeskPosition.SITTING
    assert sitting_status.position_seconds == 30
    assert standing_status.position == DeskPosition.STANDING
    assert standing_status.sitting_seconds == 37
    assert standing_status.standing_seconds == 0
    assert standing_status.position_seconds == 0
    assert continued_standing_status.standing_seconds == 10
    assert continued_standing_status.position_seconds == 10

    periods = tracker.sitting_periods.list()
    assert len(periods) == 1
    assert periods[0].position == DeskPosition.SITTING
    assert periods[0].start_at == start
    assert periods[0].end_at == start + timedelta(seconds=37)
    assert periods[0].duration_seconds == 37


def test_returning_to_sitting_resets_position_timer_and_keeps_cumulative_totals():
    tracker = DeskTracker(
        TimerProfile(
            seated_max_height_cm=70,
            standing_min_height_cm=100,
            position_confirmation_seconds=5,
        )
    )
    start = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    tracker.record(HeightReading(height_cm=65, recorded_at=start))
    tracker.record(HeightReading(height_cm=65, recorded_at=start + timedelta(seconds=60)))
    tracker.record(HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=61)))
    standing_status = tracker.record(
        HeightReading(height_cm=110, recorded_at=start + timedelta(seconds=66))
    )
    tracker.record(HeightReading(height_cm=65, recorded_at=start + timedelta(seconds=67)))
    sitting_status = tracker.record(
        HeightReading(height_cm=65, recorded_at=start + timedelta(seconds=72))
    )
    continued_sitting_status = tracker.record(
        HeightReading(height_cm=65, recorded_at=start + timedelta(seconds=82))
    )

    assert standing_status.position == DeskPosition.STANDING
    assert standing_status.sitting_seconds == 66
    assert standing_status.standing_seconds == 0
    assert standing_status.position_seconds == 0
    assert sitting_status.position == DeskPosition.SITTING
    assert sitting_status.sitting_seconds == 66
    assert sitting_status.standing_seconds == 6
    assert sitting_status.position_seconds == 0
    assert continued_sitting_status.sitting_seconds == 76
    assert continued_sitting_status.standing_seconds == 6
    assert continued_sitting_status.position_seconds == 10

    periods = tracker.sitting_periods.list()
    assert len(periods) == 2
    assert periods[0].position == DeskPosition.SITTING
    assert periods[0].start_at == start
    assert periods[0].end_at == start + timedelta(seconds=66)
    assert periods[0].duration_seconds == 66
    assert periods[1].position == DeskPosition.STANDING
    assert periods[1].start_at == start + timedelta(seconds=66)
    assert periods[1].end_at == start + timedelta(seconds=72)
    assert periods[1].duration_seconds == 6


def test_out_of_order_reading_is_rejected_without_changing_tracking_state():
    tracker = DeskTracker()
    recorded_at = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    tracker.record(HeightReading(height_cm=65, recorded_at=recorded_at))

    with pytest.raises(ValueError, match="recorded_at cannot precede"):
        tracker.record(
            HeightReading(height_cm=110, recorded_at=recorded_at - timedelta(seconds=1))
        )

    assert tracker.last_reading_at == recorded_at
    assert tracker.position == DeskPosition.SITTING
    assert len(tracker.measurements.list()) == 1
