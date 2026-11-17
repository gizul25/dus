import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient

from app.periods import record_transition
from app.desk_tracking import HeightReading


@pytest.fixture
def db():
    with MongoClient(os.environ["MONGODB_URL"]) as mongo:
        yield mongo["testdb"]


@pytest.fixture
def test_user(db):
    db["users"].replace_one(
        {"_id": "test-user"},
        {
            "_id": "test-user",
            "first_name": "Testing",
            "last_name": "User",
            "email": "user@example.com",
            "password": PasswordHasher().hash("test123"),
            "role": "user",
            "desk_id": "D-01",
        },
        upsert=True,
    )


def _reading(minutes_ago: int, desk_id: str | None = None) -> HeightReading:
    return HeightReading(
        height_cm=110,
        recorded_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
        desk_id=desk_id,
    )


def test_first_reading_opens_period(db, test_user):
    effective = record_transition(db, "test-user", _reading(0), "sitting")
    assert effective == "D-01"

    open_periods = list(db["periods"].find({"user_id": "test-user", "ended_at": None}))
    assert len(open_periods) == 1
    assert open_periods[0]["desk_id"] == "D-01"
    assert open_periods[0]["position"] == "sitting"


def test_position_change_closes_and_opens(db, test_user):
    record_transition(db, "test-user", _reading(20), "sitting")
    record_transition(db, "test-user", _reading(0),  "standing")

    open_periods = list(db["periods"].find({"user_id": "test-user", "ended_at": None}))
    assert len(open_periods) == 1
    assert open_periods[0]["position"] == "standing"

    closed = list(db["periods"].find({"user_id": "test-user", "ended_at": {"$ne": None}}))
    assert len(closed) == 1
    assert closed[0]["position"] == "sitting"


def test_desk_switch_closes_and_opens(db, test_user):
    record_transition(db, "test-user", _reading(20, desk_id="D-01"), "sitting")
    record_transition(db, "test-user", _reading(0,  desk_id="D-03"), "sitting")

    open_periods = list(db["periods"].find({"user_id": "test-user", "ended_at": None}))
    assert len(open_periods) == 1
    assert open_periods[0]["desk_id"] == "D-03"

    user = db["users"].find_one({"_id": "test-user"})
    assert user["desk_id"] == "D-03"


def test_reading_without_desk_uses_user_pointer(db, test_user):
    effective = record_transition(db, "test-user", _reading(0), "sitting")
    assert effective == "D-01"


def test_reading_without_desk_does_not_clear_pointer(db, test_user):
    record_transition(db, "test-user", _reading(0), "sitting")
    user = db["users"].find_one({"_id": "test-user"})
    assert user["desk_id"] == "D-01"