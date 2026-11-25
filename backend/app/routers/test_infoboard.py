import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient


def _utc_today_start() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


@pytest.fixture
def db(client):
    with MongoClient(os.environ["MONGODB_URL"]) as mongo:
        yield mongo["testdb"]


@pytest.fixture
def test_user(db):
    password = "test123"
    user = {
        "_id": "test-user",
        "first_name": "Testing",
        "last_name": "User",
        "email": "user@example.com",
        "password": PasswordHasher().hash(password),
        "role": "user",
    }
    db["users"].insert_one(user)
    return user


@pytest.fixture
def test_desk(db):
    db["desks"].replace_one(
        {"_id": "D-01"},
        {"_id": "D-01", "name": "Desk 1"},
        upsert=True,
    )


@pytest.fixture
def seed_period(db):
    def _seed(
        user_id: str,
        desk_id: str | None = None,
        position: str = "sitting",
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        temperature_c: float | None = None,
        humidity_pct: float | None = None,
        light: float | None = None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "desk_id": desk_id,
            "position": position,
            "started_at": (
                started_at if started_at is not None else (now - timedelta(minutes=30))
            ),
            "ended_at": ended_at,
            "temperature_c": temperature_c,
            "humidity_pct": humidity_pct,
            "light": light,
        }
        db["periods"].insert_one(doc)
        return doc

    return _seed


@pytest.fixture
def seed_session(db):
    def _seed(
        user_id: str,
        desk_id: str,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        status: str = "online",
    ) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "desk_id": desk_id,
            "status": status,
            "started_at": (
                started_at if started_at is not None else (now - timedelta(minutes=30))
            ),
            "finished_at": finished_at,
            "finished_reason": "checkout" if finished_at else None,
            "timeout_notification_at": None,
            "timeout_action_at": None,
            "timeout_notification_timer_id": None,
            "timeout_action_timer_id": None,
            "last_activity_at": now,
        }
        db["desk_sessions"].insert_one(doc)
        return doc

    return _seed


def _today_start() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


@pytest.fixture
def seed_desk(db):
    def _seed(desk_id: str, name: str | None = None) -> dict:
        doc = {"_id": desk_id, "name": name or desk_id}
        db["desks"].insert_one(doc)
        return doc

    return _seed


@pytest.fixture
def seed_error(db):
    def _seed(
        desk_id: str | None = None, severity: str = "error", message: str = "boom"
    ) -> dict:
        doc = {
            "_id": str(uuid.uuid4()),
            "message": message,
            "source": "manual",
            "severity": severity,
            "context": {"desk_id": desk_id} if desk_id else {},
            "received_at": datetime.now(timezone.utc),
        }
        db["frontend_errors"].insert_one(doc)
        return doc

    return _seed


async def login_user(client):
    response = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "test123", "mode": "user"},
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_infoboard_me_requires_auth(client):
    response = await client.get("/infoboard/me")
    print(response.text)
    assert response.status_code == 401


@pytest.mark.anyio
async def test_infoboard_me_empty(client, test_user):
    await login_user(client)

    response = await client.get("/infoboard/me")
    print(response.text)
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "test-user"
    assert body["name"] == "Testing User"
    assert body["standing_min"] == 0
    assert body["sitting_min"] == 0
    assert body["desk_id"] is None


@pytest.mark.anyio
async def test_infoboard_me_today_totals(client, test_user, seed_period):
    today = _utc_today_start()
    seed_period(
        user_id="test-user",
        position="sitting",
        started_at=today + timedelta(minutes=10),
        ended_at=today + timedelta(minutes=40),
    )
    seed_period(
        user_id="test-user",
        position="standing",
        started_at=today + timedelta(minutes=40),
        ended_at=today + timedelta(minutes=60),
    )

    await login_user(client)
    response = await client.get("/infoboard/me")
    print(response.text)
    assert response.status_code == 200
    body = response.json()
    assert body["sitting_min"] == 30
    assert body["standing_min"] == 20


@pytest.mark.anyio
async def test_infoboard_me_open_period_sets_desk_id(client, test_user, seed_session):
    now = datetime.now(timezone.utc)
    seed_session(
        user_id="test-user",
        desk_id="D-42",
        status="online",
        started_at=now - timedelta(minutes=10),
        finished_at=None,
    )

    await login_user(client)
    response = await client.get("/infoboard/me")
    print(response.text)
    assert response.status_code == 200
    body = response.json()
    assert body["desk_id"] == "D-42"
    assert body["status"] == "online"


@pytest.mark.anyio
async def test_infoboard_me_period_without_session_has_no_desk_id(
    client,
    test_user,
    seed_period,
):
    now = datetime.now(timezone.utc)
    seed_period(
        user_id="test-user",
        desk_id="D-42",
        position="standing",
        started_at=now - timedelta(minutes=10),
        ended_at=None,
    )

    await login_user(client)
    body = (await client.get("/infoboard/me")).json()
    assert body["desk_id"] is None
    assert body["status"] is None


@pytest.mark.anyio
async def test_infoboard_me_ignores_yesterday(client, test_user, seed_period):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    seed_period(
        user_id="test-user",
        position="sitting",
        started_at=yesterday_start,
        ended_at=yesterday_start + timedelta(hours=2),
    )

    await login_user(client)
    response = await client.get("/infoboard/me")
    print(response.text)
    body = response.json()
    assert body["sitting_min"] == 0
    assert body["standing_min"] == 0


@pytest.mark.anyio
async def test_infoboard_me_isolated_per_user(client, test_user, seed_period):
    today = _utc_today_start()
    seed_period(
        user_id="somebody-else",
        position="sitting",
        started_at=today + timedelta(minutes=10),
        ended_at=today + timedelta(minutes=70),
    )
    seed_period(
        user_id="test-user",
        position="standing",
        started_at=today + timedelta(minutes=70),
        ended_at=today + timedelta(minutes=85),
    )

    await login_user(client)
    response = await client.get("/infoboard/me")
    print(response.text)
    body = response.json()
    assert body["sitting_min"] == 0
    assert body["standing_min"] == 15


@pytest.mark.anyio
async def test_infoboard_desks_empty(client, test_user):
    await login_user(client)

    response = await client.get("/infoboard/desks")
    print(response.text)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_infoboard_desks_aggregates(
    client, db, test_user, seed_desk, seed_session, seed_period
):
    today = _today_start()
    seed_desk("D-01", "Alpha")
    seed_desk("D-02", "Beta")

    seed_session(
        "u1",
        "D-01",
        started_at=today + timedelta(minutes=10),
        finished_at=today + timedelta(minutes=70),
    )
    seed_session(
        "u1",
        "D-01",
        started_at=today + timedelta(minutes=80),
        finished_at=today + timedelta(minutes=110),
    )

    seed_session(
        "u2",
        "D-02",
        started_at=today + timedelta(minutes=20),
        finished_at=today + timedelta(minutes=65),
    )

    seed_period(
        "u1",
        "D-01",
        "sitting",
        started_at=today + timedelta(minutes=10),
        ended_at=today + timedelta(minutes=70),
        temperature_c=22.0,
        humidity_pct=45.0,
        light=0.50,
    )

    await login_user(client)
    response = await client.get("/infoboard/desks")
    print(response.text)
    assert response.status_code == 200
    rows = {r["id"]: r for r in response.json()}

    assert rows["D-01"]["time_used_min"] == 90.0
    assert rows["D-01"]["unique_users"] == 1
    assert rows["D-02"]["time_used_min"] == 45.0
    assert rows["D-02"]["unique_users"] == 1

    assert rows["D-01"]["temperature"] == 22.0
    assert rows["D-01"]["humidity"] == 45.0
    assert rows["D-01"]["light"] == 0.5

    assert "avg_sit_min" not in rows["D-01"]
    assert "avg_stand_min" not in rows["D-01"]


@pytest.mark.anyio
async def test_infoboard_desks_occupied_flag(
    client, test_user, seed_desk, seed_session
):
    now = datetime.now(timezone.utc)
    seed_desk("D-01")
    seed_desk("D-02")
    seed_session(
        "u1",
        "D-01",
        status="online",
        started_at=now - timedelta(minutes=5),
        finished_at=None,
    )

    await login_user(client)
    response = await client.get("/infoboard/desks")
    print(response.text)
    assert response.status_code == 200
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["occupied"] is True
    assert rows["D-02"]["occupied"] is False


@pytest.mark.anyio
async def test_infoboard_desks_errors_and_warnings(
    client, test_user, seed_desk, seed_error
):
    seed_desk("D-01")
    seed_desk("D-02")
    seed_error("D-01", severity="error")
    seed_error("D-01", severity="error")
    seed_error("D-01", severity="warning")
    seed_error("D-02", severity="warning")

    await login_user(client)
    response = await client.get("/infoboard/desks")
    print(response.text)
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["errors"] == 2
    assert rows["D-01"]["warnings"] == 1
    assert rows["D-02"]["errors"] == 0
    assert rows["D-02"]["warnings"] == 1


@pytest.mark.anyio
async def test_infoboard_desks_ignores_errors_without_desk_id(
    client, test_user, seed_desk, seed_error
):
    seed_desk("D-01")
    seed_error(None, severity="error")
    seed_error("D-01", severity="error")

    await login_user(client)
    response = await client.get("/infoboard/desks")
    print(response.text)
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["errors"] == 1


@pytest.mark.anyio
async def test_infoboard_desks_environmental_averages(
    client,
    test_user,
    seed_desk,
    seed_period,
):
    now = datetime.now(timezone.utc)
    seed_desk("D-01")
    seed_period(
        "u1",
        "D-01",
        "sitting",
        started_at=now - timedelta(minutes=10),
        ended_at=now,
        temperature_c=22.0,
        humidity_pct=45.0,
        light=0.40,
    )
    seed_period(
        "u1",
        "D-01",
        "standing",
        started_at=now - timedelta(minutes=5),
        ended_at=now,
        temperature_c=24.0,
        humidity_pct=55.0,
        light=0.80,
    )

    await login_user(client)
    response = await client.get("/infoboard/desks?timeframe=all")
    print(response.text)
    assert response.status_code == 200
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["temperature"] == 23.0
    assert rows["D-01"]["humidity"] == 50.0
    assert rows["D-01"]["light"] == 0.6


@pytest.mark.anyio
async def test_infoboard_desks_environmental_averages_ignore_missing_fields(
    client, test_user, seed_desk, seed_period
):
    now = datetime.now(timezone.utc)
    seed_desk("D-01")
    seed_period(
        "u1",
        "D-01",
        "sitting",
        started_at=now - timedelta(minutes=60),
        ended_at=now - timedelta(minutes=30),
        temperature_c=22.0,
    )
    seed_period(
        "u1",
        "D-01",
        "sitting",
        started_at=now - timedelta(minutes=10),
        ended_at=now,
        temperature_c=24.0,
        humidity_pct=55.0,
        light=0.55,
    )

    await login_user(client)
    response = await client.get("/infoboard/desks?timeframe=all")
    print(response.text)
    assert response.status_code == 200
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["temperature"] == 23.0
    assert rows["D-01"]["humidity"] == 55.0
    assert rows["D-01"]["light"] == 0.55


@pytest.mark.anyio
async def test_infoboard_me_desk_id_from_session_not_period(
    client, db, test_user, test_desk
):
    await login_user(client)
    await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})

    me = (await client.get("/infoboard/me")).json()
    assert me["desk_id"] == "D-01"
    assert me["sitting_min"] == 0 and me["standing_min"] == 0


@pytest.mark.anyio
async def test_infoboard_desks_occupied_clears_after_check_out(
    client, db, test_user, test_desk
):
    await login_user(client)
    await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})
    assert (await client.get("/infoboard/desks")).json()[0]["occupied"] is True

    sid = (await client.get("/desk-sessions/user/test-user")).json()["id"]
    await client.post(f"/desk-sessions/{sid}/check-out")
    assert (await client.get("/infoboard/desks")).json()[0]["occupied"] is False


@pytest.mark.anyio
async def test_infoboard_desks_timeframe_filters(
    client, test_user, seed_desk, seed_session
):
    now = datetime.now(timezone.utc)
    today = _today_start()
    seed_desk("D-01")

    seed_session(
        "u1",
        "D-01",
        started_at=today + timedelta(minutes=10),
        finished_at=today + timedelta(minutes=70),
    )
    seed_session(
        "u1",
        "D-01",
        started_at=now - timedelta(days=10),
        finished_at=now - timedelta(days=10) + timedelta(minutes=120),
    )

    await login_user(client)

    today_rows = {
        r["id"]: r
        for r in (await client.get("/infoboard/desks?timeframe=today")).json()
    }
    assert today_rows["D-01"]["time_used_min"] == 60.0

    all_rows = {
        r["id"]: r for r in (await client.get("/infoboard/desks?timeframe=all")).json()
    }
    assert all_rows["D-01"]["time_used_min"] == 180.0


@pytest.mark.anyio
async def test_infoboard_desks_unique_users_counts_distinct_users(
    client, test_user, seed_desk, seed_session
):
    today = _today_start()
    seed_desk("D-01")

    seed_session(
        "u1",
        "D-01",
        started_at=today + timedelta(minutes=10),
        finished_at=today + timedelta(minutes=40),
    )
    seed_session(
        "u1",
        "D-01",
        started_at=today + timedelta(minutes=50),
        finished_at=today + timedelta(minutes=80),
    )
    seed_session(
        "u2",
        "D-01",
        started_at=today + timedelta(minutes=90),
        finished_at=today + timedelta(minutes=120),
    )

    await login_user(client)
    rows = {r["id"]: r for r in (await client.get("/infoboard/desks")).json()}
    assert rows["D-01"]["unique_users"] == 2
    assert rows["D-01"]["time_used_min"] == 90.0
