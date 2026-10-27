from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Supported desk positions
class DeskPosition(StrEnum):
    SITTING = "sitting"
    STANDING = "standing"


# User-specific timer settings and height thresholds
class TimerProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seated_max_height_cm: float = Field(default=75, gt=0, le=200)
    standing_min_height_cm: float = Field(default=95, gt=0, le=200)
    sitting_target_minutes: int = Field(default=30, gt=0, le=480)
    standing_target_minutes: int = Field(default=10, gt=0, le=480)

    # Ensure sitting and standing height ranges do not overlap
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


# Represents a single height measurement
class HeightReading(BaseModel):
    height_cm: float = Field(gt=0, le=200)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Assign UTC to timestamps without a timezone
    @field_validator("recorded_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


# Represents the current status of the desk, including position, time spent, and target times
class DeskStatus(BaseModel):
    height_cm: float | None
    position: DeskPosition | None
    sitting_seconds: float
    standing_seconds: float
    position_seconds: float
    target_seconds: int | None
    timer_overdue: bool
    last_reading_at: datetime | None


# Tracks the desk's position and time spent in each position based on height readings
class DeskTracker:
    def __init__(self, profile: TimerProfile | None = None):
        # Use the provided profile or default settings
        self.profile = profile or TimerProfile()

        # Initialize the current desk state
        self.height_cm: float | None = None
        self.position: DeskPosition | None = None

        # Initialize time counters
        self.sitting_seconds = 0.0
        self.standing_seconds = 0.0
        self.position_seconds = 0.0

        # Store the timestamp of the last measurement
        self.last_reading_at: datetime | None = None

    # Update the user's timer settings
    def update_profile(self, profile: TimerProfile) -> None:
        self.profile = profile

    # Process a new height measurement and update the desk status
    def record(self, reading: HeightReading) -> DeskStatus:
        # Calculate elapsed time since the previous measurement
        if self.last_reading_at is not None:
            # Reject measurements received out of chronological order
            if reading.recorded_at < self.last_reading_at:
                raise ValueError("recorded_at cannot precede the previous reading")

            elapsed = (reading.recorded_at - self.last_reading_at).total_seconds()

            # Add elapsed time to the previous position's counters
            if self.position == DeskPosition.SITTING:
                self.sitting_seconds += elapsed
                self.position_seconds += elapsed
            elif self.position == DeskPosition.STANDING:
                self.standing_seconds += elapsed
                self.position_seconds += elapsed

        # Determine the position from the new height
        classified = self._classify(reading.height_cm)

        # Reset the position timer when the position changes
        if classified is not None and classified != self.position:
            self.position = classified
            self.position_seconds = 0.0

        # Store the latest measurement
        self.height_cm = reading.height_cm
        self.last_reading_at = reading.recorded_at

        return self.status()

    # Build a status summary with the current timer information
    def status(self) -> DeskStatus:
        target_seconds = None

        # Select the target duration for the current position
        if self.position == DeskPosition.SITTING:
            target_seconds = self.profile.sitting_target_minutes * 60
        elif self.position == DeskPosition.STANDING:
            target_seconds = self.profile.standing_target_minutes * 60

        # Return the current state and timer progress
        return DeskStatus(
            height_cm=self.height_cm,
            position=self.position,
            sitting_seconds=self.sitting_seconds,
            standing_seconds=self.standing_seconds,
            position_seconds=self.position_seconds,
            target_seconds=target_seconds,
            timer_overdue=(target_seconds is not None and self.position_seconds >= target_seconds),
            last_reading_at=self.last_reading_at,
        )

    # Classify desk position using the configured height thresholds
    def _classify(self, height_cm: float) -> DeskPosition | None:
        if height_cm <= self.profile.seated_max_height_cm:
            return DeskPosition.SITTING
        if height_cm >= self.profile.standing_min_height_cm:
            return DeskPosition.STANDING

        # Return None when the height is between the sitting and standing thresholds
        return None
