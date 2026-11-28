import os

import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient


# ───────────────────────────────────────────────────── fixtures


@pytest.fixture
def db(client):                                   # `client` is required so pytest runs
    with MongoClient(os.environ["MONGODB_URL"]) as mongo:   # conftest cleanup first
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
def test_admin(db):
    db["users"].replace_one(
        {"_id": "test-admin"},
        {
            "_id": "test-admin",
            "first_name": "Testing",
            "last_name": "Admin",
            "email": "admin@example.com",
            "password": PasswordHasher().hash("test123"),
            "role": "admin",
        },
        upsert=True,
    )


@pytest.fixture
def test_desk(db):
    db["desks"].replace_one(
        {"_id": "D-01"}, {"_id": "D-01", "name": "Desk 1"}, upsert=True,
    )


# ───────────────────────────────────────────────────── helper


async def _login(client, email="user@example.com", mode="user"):
    r = await client.post(
        "/auth/login",
        json={"email": email, "password": "test123", "mode": mode},
    )
    assert r.status_code == 200, r.text


# ───────────────────────────────────────────────────── tests


@pytest.mark.anyio
async def test_check_in_creates_session(client, db, test_user, test_desk):
    await _login(client)
    r = await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["user_id"] == "test-user"
    assert body["desk_id"] == "D-01"
    assert body["status"] == "online"
    assert body["finished_at"] is None


@pytest.mark.anyio
async def test_check_in_twice_is_409(client, test_user, test_desk):
    await _login(client)
    first = await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})
    assert first.status_code == 201, first.text

    second = await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})
    assert second.status_code == 409


@pytest.mark.anyio
async def test_status_transitions(client, test_user, test_desk):
    await _login(client)
    s = (await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})).json()

    r = await client.patch(f"/desk-sessions/{s['id']}/status", json={"status": "away"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "away"

    r = await client.patch(f"/desk-sessions/{s['id']}/status",
                           json={"status": "do not disturb"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "do not disturb"


@pytest.mark.anyio
async def test_check_out_marks_finished(client, test_user, test_desk):
    await _login(client)
    s = (await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})).json()

    r = await client.post(f"/desk-sessions/{s['id']}/check-out")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["finished_at"] is not None
    assert body["finished_reason"] == "checkout"
    assert body["status"] == "offline"


@pytest.mark.anyio
async def test_check_out_is_idempotent(client, test_user, test_desk):
    await _login(client)
    s = (await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})).json()
    a = await client.post(f"/desk-sessions/{s['id']}/check-out")
    b = await client.post(f"/desk-sessions/{s['id']}/check-out")
    assert a.status_code == 200 and b.status_code == 200
    assert a.json()["finished_at"] == b.json()["finished_at"]


@pytest.mark.anyio
async def test_check_out_desk_ends_all_open_sessions(
    client, db, test_user, test_admin, test_desk,          # ← test_admin added
):
    db["users"].replace_one(
        {"_id": "u2"},
        {
            "_id": "u2", "first_name": "U", "last_name": "2",
            "email": "u2@example.com",
            "password": PasswordHasher().hash("test123"),
            "role": "user",
        },
        upsert=True,
    )
    await _login(client)
    await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})
    await _login(client, email="u2@example.com")
    await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})

    await _login(client, email="admin@example.com", mode="admin")
    r = await client.post("/desk-sessions/desk/D-01/check-out")
    assert r.status_code == 200, r.text
    assert len(r.json()) == 2
    assert db["desk_sessions"].count_documents(
        {"desk_id": "D-01", "finished_at": None}
    ) == 0


@pytest.mark.anyio
async def test_cannot_view_other_users_session(
    client, test_user, test_admin, test_desk,
):
    await _login(client, email="admin@example.com", mode="admin")
    await client.post("/desk-sessions/check-in", json={"desk_id": "D-01"})

    await _login(client)                       # back to test-user
    r = await client.get("/desk-sessions/user/test-admin")
    assert r.status_code == 403


@pytest.mark.anyio
async def test_list_sessions_admin_only(client, test_user, test_admin):
    await _login(client)
    r = await client.get("/desk-sessions/")
    assert r.status_code == 403, r.text

    await _login(client, email="admin@example.com", mode="admin")
    r = await client.get("/desk-sessions/")
    assert r.status_code == 200, r.text