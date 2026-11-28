import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient

from app.desk_tracking import HeightReading
from app.periods import record_transition

# ─────────────────────────────────────────────────────── fixtures


@pytest.fixture
def db(client):
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
        },
        upsert=True,
    )


@pytest.fixture
def open_session(db):
    def _open(desk_id: str = "D-01", user_id: str = "test-user") -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "desk_id": desk_id,
            "status": "online",
            "started_at": now - timedelta(minutes=30),
            "finished_at": None,
            "finished_reason": None,
            "timeout_notification_at": None,
            "timeout_action_at": None,
            "timeout_notification_timer_id": None,
            "timeout_action_timer_id": None,
            "last_activity_at": now,
        }
        db["desk_sessions"].insert_one(doc)
        return doc
    return _open


def _reading(minutes_ago: int = 0, height_cm: float = 110) -> HeightReading:
    return HeightReading(
        height_cm=height_cm,
        recorded_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
    )


# ─────────────────────────────────────────────────── first reading


@pytest.mark.anyio
async def test_first_reading_opens_period(client, db, test_user, open_session):
    session = open_session("D-01")

    result = record_transition(db, "test-user", _reading(0), "sitting")

    assert result == "D-01"
    periods = list(db["periods"].find({"user_id": "test-user"}))
    assert len(periods) == 1
    p = periods[0]
    assert p["desk_id"] == "D-01"
    assert p["position"] == "sitting"
    assert p["ended_at"] is None
    assert p["session_id"] == session["_id"]


@pytest.mark.anyio
async def test_reading_timestamp_used_for_started_at(client, db, test_user, open_session):
    open_session("D-01")
    reading = _reading(15)
    record_transition(db, "test-user", reading, "sitting")

    p = db["periods"].find_one({"user_id": "test-user"})
    started = p["started_at"].replace(tzinfo=timezone.utc)
    assert abs((started - reading.recorded_at).total_seconds()) < 0.01


# ────────────────────────────────────────────────────── skip cases


@pytest.mark.anyio
async def test_reading_without_session_is_skipped(client, db, test_user):
    result = record_transition(db, "test-user", _reading(0), "sitting")

    assert result is None
    assert db["periods"].count_documents({"user_id": "test-user"}) == 0


@pytest.mark.anyio
async def test_two_skips_leave_collection_empty(client, db, test_user):
    record_transition(db, "test-user", _reading(5), "sitting")
    record_transition(db, "test-user", _reading(0), "standing")

    assert db["periods"].count_documents({"user_id": "test-user"}) == 0


@pytest.mark.anyio
async def test_session_without_desk_is_skipped(client, db, test_user, open_session):
    open_session("D-01")
    db["desk_sessions"].update_one(
        {"user_id": "test-user", "finished_at": None},
        {"$set": {"desk_id": None}},
    )

    result = record_transition(db, "test-user", _reading(0), "sitting")
    assert result is None
    assert db["periods"].count_documents({"user_id": "test-user"}) == 0


# ─────────────────────────────────────────────────────── transitions


@pytest.mark.anyio
async def test_position_change_closes_and_opens(client, db, test_user, open_session):
    open_session("D-01")
    record_transition(db, "test-user", _reading(20), "sitting")
    record_transition(db, "test-user", _reading(0), "standing")

    open_periods = list(db["periods"].find({"user_id": "test-user", "ended_at": None}))
    assert len(open_periods) == 1
    assert open_periods[0]["position"] == "standing"

    closed = list(db["periods"].find({"user_id": "test-user", "ended_at": {"$ne": None}}))
    assert len(closed) == 1
    assert closed[0]["position"] == "sitting"


@pytest.mark.anyio
async def test_same_state_does_not_duplicate(client, db, test_user, open_session):
    open_session("D-01")
    record_transition(db, "test-user", _reading(10), "sitting")
    record_transition(db, "test-user", _reading(5), "sitting")
    record_transition(db, "test-user", _reading(0), "sitting")

    assert db["periods"].count_documents({"user_id": "test-user"}) == 1


@pytest.mark.anyio
async def test_desk_switch_via_new_session_closes_and_opens(client, db, test_user, open_session):
    s1 = open_session("D-01")
    record_transition(db, "test-user", _reading(20), "sitting")

    db["desk_sessions"].update_one(
        {"_id": s1["_id"]},
        {"$set": {
            "finished_at": datetime.now(timezone.utc),
            "finished_reason": "checkout",
        }},
    )

    open_session("D-03")
    result = record_transition(db, "test-user", _reading(0), "sitting")
    assert result == "D-03"

    open_periods = list(db["periods"].find({"user_id": "test-user", "ended_at": None}))
    assert len(open_periods) == 1
    assert open_periods[0]["desk_id"] == "D-03"
    assert open_periods[0]["session_id"] != s1["_id"]

    closed = list(db["periods"].find({"user_id": "test-user", "ended_at": {"$ne": None}}))
    assert len(closed) == 1
    assert closed[0]["desk_id"] == "D-01"