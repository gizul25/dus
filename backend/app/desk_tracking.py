from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DeskPosition(StrEnum):
    SITTING = "sitting"
    STANDING = "standing"


class TimerProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seated_max_height_cm: float = Field(default=75, gt=0, le=200)
    standing_min_height_cm: float = Field(default=95, gt=0, le=200)
    sitting_target_minutes: int = Field(default=30, gt=0, le=480)
    standing_target_minutes: int = Field(default=10, gt=0, le=480)
    position_confirmation_seconds: int = Field(default=5, ge=0, le=300)

    @model_validator(mode="after")
    def validate_height_thresholds(self) -> "TimerProfile":
        if self.seated_max_height_cm >= self.standing_min_height_cm:
            raise ValueError("standing_min_height_cm must exceed seated_max_height_cm")
        return self


class TimerProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80)
    settings: TimerProfile


class NamedTimerProfile(TimerProfileInput):
    profile_id: str


class TimerProfileRegistry:
    def __init__(self, default_settings: TimerProfile | None = None):
        default = NamedTimerProfile(
            profile_id="default",
            name="Default",
            settings=default_settings or TimerProfile(),
        )
        self._profiles: dict[str, NamedTimerProfile] = {default.profile_id: default}
        self.active_profile_id = default.profile_id

    def list_profiles(self) -> list[NamedTimerProfile]:
        return list(self._profiles.values())

    def get_profile(self, profile_id: str) -> NamedTimerProfile | None:
        return self._profiles.get(profile_id)

    def create_profile(self, profile: TimerProfileInput) -> NamedTimerProfile:
        profile_id = str(uuid4())
        saved = NamedTimerProfile(profile_id=profile_id, **profile.model_dump())
        self._profiles[profile_id] = saved
        return saved

    def update_profile(self, profile_id: str, profile: TimerProfileInput) -> NamedTimerProfile | None:
        if profile_id not in self._profiles:
            return None
        saved = NamedTimerProfile(profile_id=profile_id, **profile.model_dump())
        self._profiles[profile_id] = saved
        return saved

    def delete_profile(self, profile_id: str) -> bool:
        if profile_id == "default" or profile_id == self.active_profile_id:
            return False
        return self._profiles.pop(profile_id, None) is not None

    def activate_profile(self, profile_id: str) -> NamedTimerProfile | None:
        profile = self._profiles.get(profile_id)
        if profile is not None:
            self.active_profile_id = profile_id
        return profile


class HeightReading(BaseModel):
    height_cm: float = Field(gt=0, le=200)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("recorded_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class SittingPeriod(BaseModel):
    start_at: datetime
    end_at: datetime | None = None
    duration_seconds: float = 0.0
    position: DeskPosition = DeskPosition.SITTING


class MeasurementRepository:
    def __init__(self):
        self._measurements: list[HeightReading] = []

    def add(self, reading: HeightReading) -> None:
        self._measurements.append(reading)

    def list(self, limit: int | None = None) -> list[HeightReading]:
        items = list(self._measurements)
        if limit is not None:
            return items[-limit:]
        return items

    def latest(self) -> HeightReading | None:
        if not self._measurements:
            return None
        return self._measurements[-1]


class SittingPeriodRepository:
    def __init__(self):
        self._periods: list[SittingPeriod] = []

    def add(self, period: SittingPeriod) -> None:
        self._periods.append(period)

    def list(self, limit: int | None = None) -> list[SittingPeriod]:
        items = list(self._periods)
        if limit is not None:
            return items[-limit:]
        return items


class DeskStatus(BaseModel):
    height_cm: float | None
    position: DeskPosition | None
    sitting_seconds: float
    standing_seconds: float
    position_seconds: float
    target_seconds: int | None
    timer_overdue: bool
    reminder_due: bool
    last_reading_at: datetime | None


class DeskTracker:
    def __init__(self, profile: TimerProfile | None = None):
        self.profile = profile or TimerProfile()
        self.measurements = MeasurementRepository()
        self.sitting_periods = SittingPeriodRepository()

        self.height_cm: float | None = None
        self.position: DeskPosition | None = None
        self.sitting_seconds = 0.0
        self.standing_seconds = 0.0
        self.position_seconds = 0.0
        self.last_reading_at: datetime | None = None
        self.pending_position: DeskPosition | None = None
        self.pending_position_since: datetime | None = None
        self.reminder_triggered = False
        self.current_period: SittingPeriod | None = None

    def update_profile(self, profile: TimerProfile) -> None:
        self.profile = profile

    def record(self, reading: HeightReading) -> DeskStatus:
        if self.last_reading_at is not None:
            if reading.recorded_at < self.last_reading_at:
                raise ValueError("recorded_at cannot precede the previous reading")

            elapsed = (reading.recorded_at - self.last_reading_at).total_seconds()
            if self.position == DeskPosition.SITTING:
                self.sitting_seconds += elapsed
                self.position_seconds += elapsed
            elif self.position == DeskPosition.STANDING:
                self.standing_seconds += elapsed
                self.position_seconds += elapsed

        candidate = self._classify(reading.height_cm)
        self.measurements.add(reading)

        if self.position is None and candidate is not None:
            self.position = candidate
            self.position_seconds = 0.0
            self._start_or_continue_period(candidate, reading.recorded_at)
        elif candidate is not None:
            if candidate != self.position:
                if self.pending_position != candidate or self.pending_position_since is None:
                    self.pending_position = candidate
                    self.pending_position_since = reading.recorded_at
                elif (
                    reading.recorded_at - self.pending_position_since
                ).total_seconds() >= self.profile.position_confirmation_seconds:
                    self._commit_position_change(candidate, reading.recorded_at)
            else:
                self.pending_position = None
                self.pending_position_since = None
                if self.current_period is not None and self.current_period.position != candidate:
                    self._start_or_continue_period(candidate, reading.recorded_at)

        self.height_cm = reading.height_cm
        self.last_reading_at = reading.recorded_at
        return self.status()

    def status(self) -> DeskStatus:
        target_seconds = None
        if self.position == DeskPosition.SITTING:
            target_seconds = self.profile.sitting_target_minutes * 60
        elif self.position == DeskPosition.STANDING:
            target_seconds = self.profile.standing_target_minutes * 60

        reminder_due = (
            self.position == DeskPosition.SITTING
            and target_seconds is not None
            and self.position_seconds >= target_seconds
            and not self.reminder_triggered
        )

        if self.position != DeskPosition.SITTING:
            reminder_due = False

        return DeskStatus(
            height_cm=self.height_cm,
            position=self.position,
            sitting_seconds=self.sitting_seconds,
            standing_seconds=self.standing_seconds,
            position_seconds=self.position_seconds,
            target_seconds=target_seconds,
            timer_overdue=(target_seconds is not None and self.position_seconds >= target_seconds),
            reminder_due=reminder_due,
            last_reading_at=self.last_reading_at,
        )

    def _commit_position_change(self, new_position: DeskPosition, timestamp: datetime) -> None:
        if self.current_period is not None and self.current_period.position != new_position:
            self.current_period.end_at = timestamp
            self.current_period.duration_seconds = max(
                0.0,
                (self.current_period.end_at - self.current_period.start_at).total_seconds(),
            )
            self.sitting_periods.add(self.current_period)
            self.current_period = None

        self.position = new_position
        self.position_seconds = 0.0
        self.pending_position = None
        self.pending_position_since = None
        self.reminder_triggered = False
        self._start_or_continue_period(new_position, timestamp)

    def _start_or_continue_period(self, position: DeskPosition, timestamp: datetime) -> None:
        if self.current_period is None:
            self.current_period = SittingPeriod(start_at=timestamp, position=position)
        elif self.current_period.position != position:
            self.current_period.end_at = timestamp
            self.current_period.duration_seconds = max(
                0.0,
                (self.current_period.end_at - self.current_period.start_at).total_seconds(),
            )
            self.sitting_periods.add(self.current_period)
            self.current_period = SittingPeriod(start_at=timestamp, position=position)

    def _classify(self, height_cm: float) -> DeskPosition | None:
        if height_cm <= self.profile.seated_max_height_cm:
            return DeskPosition.SITTING
        if height_cm >= self.profile.standing_min_height_cm:
            return DeskPosition.STANDING
        return None
