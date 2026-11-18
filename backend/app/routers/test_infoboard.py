import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient


def _utc_today_start() -> datetime:
    """Matches the router's `today = now.replace(hour=0, ...)` — UTC midnight."""
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
def seed_period(db):
    """Insert a `periods` doc. Returns it so tests can inspect ids if needed."""
    def _seed(
        user_id: str,
        desk_id: str | None = None,
        position: str = "sitting",
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        temperature_c: float | None = None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "desk_id": desk_id,
            "position": position,
            "started_at": started_at if started_at is not None else (now - timedelta(minutes=30)),
            "ended_at": ended_at,
            "temperature_c": temperature_c,
        }
        db["periods"].insert_one(doc)
        return doc
    return _seed


@pytest.fixture
def seed_desk(db):
    def _seed(desk_id: str, name: str | None = None) -> dict:
        doc = {"_id": desk_id, "name": name or desk_id}
        db["desks"].insert_one(doc)
        return doc
    return _seed


@pytest.fixture
def seed_error(db):
    def _seed(desk_id: str | None = None, severity: str = "error", message: str = "boom") -> dict:
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
async def test_dashboard_me_requires_auth(client):
    response = await client.get("/dashboard/me")
    print(response.text)
    assert response.status_code == 401


@pytest.mark.anyio
async def test_dashboard_me_empty(client, test_user):
    await login_user(client)

    response = await client.get("/dashboard/me")
    print(response.text)
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "test-user"
    assert body["name"] == "Testing User"
    assert body["standing_min"] == 0
    assert body["sitting_min"] == 0
    assert body["desk_id"] is None


@pytest.mark.anyio
async def test_dashboard_me_today_totals(client, test_user, seed_period):
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
    response = await client.get("/dashboard/me")
    print(response.text)
    assert response.status_code == 200
    body = response.json()
    assert body["sitting_min"] == 30
    assert body["standing_min"] == 20


@pytest.mark.anyio
async def test_dashboard_me_open_period_sets_desk_id(client, test_user, seed_period):
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    started_at = now - timedelta(minutes=10)
    if started_at < today:
        pytest.skip("Requires at least 10 minutes past UTC midnight")

    seed_period(
        user_id="test-user",
        desk_id="D-42",
        position="standing",
        started_at=started_at,
        ended_at=None,
    )

    await login_user(client)
    response = await client.get("/dashboard/me")
    print(response.text)
    assert response.status_code == 200
    body = response.json()
    assert body["desk_id"] == "D-42"
    assert body["standing_min"] == 10


@pytest.mark.anyio
async def test_dashboard_me_ignores_yesterday(client, test_user, seed_period):
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
    response = await client.get("/dashboard/me")
    print(response.text)
    body = response.json()
    assert body["sitting_min"] == 0
    assert body["standing_min"] == 0


@pytest.mark.anyio
async def test_dashboard_me_isolated_per_user(client, test_user, seed_period):
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
    response = await client.get("/dashboard/me")
    print(response.text)
    body = response.json()
    assert body["sitting_min"] == 0
    assert body["standing_min"] == 15


@pytest.mark.anyio
async def test_dashboard_desks_empty(client, test_user):
    await login_user(client)

    response = await client.get("/dashboard/desks")
    print(response.text)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_dashboard_desks_aggregates(client, test_user, seed_desk, seed_period):
    now = datetime.now(timezone.utc)
    seed_desk("D-01", "Alpha")
    seed_desk("D-02", "Beta")
    seed_period("u1", "D-01", "sitting",  started_at=now - timedelta(minutes=60), ended_at=now)
    seed_period("u1", "D-01", "standing", started_at=now - timedelta(minutes=30), ended_at=now)
    seed_period("u2", "D-02", "sitting",  started_at=now - timedelta(minutes=20), ended_at=now)

    await login_user(client)
    response = await client.get("/dashboard/desks")
    print(response.text)
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 2

    by_id = {r["id"]: r for r in rows}
    assert by_id["D-01"]["name"] == "Alpha"
    assert by_id["D-01"]["avg_sit_min"] == 60.0
    assert by_id["D-01"]["avg_stand_min"] == 30.0
    assert by_id["D-02"]["name"] == "Beta"
    assert by_id["D-02"]["avg_sit_min"] == 20.0
    assert by_id["D-02"]["avg_stand_min"] == 0.0


@pytest.mark.anyio
async def test_dashboard_desks_occupied_flag(client, test_user, seed_desk, seed_period):
    now = datetime.now(timezone.utc)
    seed_desk("D-01")
    seed_desk("D-02")
    seed_period("u1", "D-01", "sitting", started_at=now - timedelta(minutes=5), ended_at=None)

    await login_user(client)
    response = await client.get("/dashboard/desks")
    print(response.text)
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["occupied"] is True
    assert rows["D-02"]["occupied"] is False


@pytest.mark.anyio
async def test_dashboard_desks_errors_and_warnings(client, test_user, seed_desk, seed_error):
    seed_desk("D-01")
    seed_desk("D-02")
    seed_error("D-01", severity="error")
    seed_error("D-01", severity="error")
    seed_error("D-01", severity="warning")
    seed_error("D-02", severity="warning")

    await login_user(client)
    response = await client.get("/dashboard/desks")
    print(response.text)
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["errors"] == 2
    assert rows["D-01"]["warnings"] == 1
    assert rows["D-02"]["errors"] == 0
    assert rows["D-02"]["warnings"] == 1


@pytest.mark.anyio
async def test_dashboard_desks_ignores_errors_without_desk_id(client, test_user, seed_desk, seed_error):
    seed_desk("D-01")
    seed_error(None, severity="error")   
    seed_error("D-01", severity="error")

    await login_user(client)
    response = await client.get("/dashboard/desks")
    print(response.text)
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["errors"] == 1


@pytest.mark.anyio
async def test_dashboard_desks_temperature_average(client, test_user, seed_desk, seed_period):
    now = datetime.now(timezone.utc)
    seed_desk("D-01")
    seed_period("u1", "D-01", "sitting", started_at=now - timedelta(minutes=10), ended_at=now, temperature_c=22.0)
    seed_period("u1", "D-01", "sitting", started_at=now - timedelta(minutes=5),  ended_at=now, temperature_c=24.0)

    await login_user(client)
    response = await client.get("/dashboard/desks")
    print(response.text)
    rows = {r["id"]: r for r in response.json()}
    assert rows["D-01"]["temperature"] == 23.0