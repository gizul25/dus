import os
from datetime import timedelta
import jwt
import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient
from app.dependencies import JWT_SECRET, JWT_ALGORITHM
from app.routers.auth import create_token


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
def test_admin(db):
    password = "test123"
    user = {
        "_id": "test-admin",
        "first_name": "Testing",
        "last_name": "Admin",
        "email": "admin@example.com",
        "password": PasswordHasher().hash(password),
        "role": "admin",
    }
    db["users"].insert_one(user)
    return user


@pytest.mark.anyio
async def test_login_valid_credentials(client, test_user):
    response = await client.post(
        "/auth/login", json={"email": "user@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies

    token = response.cookies["access_token"]
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["mode"] == "user"


@pytest.mark.anyio
async def test_login_invalid_password(client, test_user):
    response = await client.post(
        "/auth/login", json={"email": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_invalid_email(client, test_user):
    response = await client.post(
        "/auth/login", json={"email": "User@example.com", "password": "test123"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_checked_remember_me(client, test_user):
    response = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "test123", "remember_me": True},
    )
    expected_duration = timedelta(days=30)
    assert (
        f"Max-Age={int(expected_duration.total_seconds())}"
        in response.headers["set-cookie"]
    )


@pytest.mark.anyio
async def test_unchecked_remember_me(client, test_user):
    response = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "test123", "remember_me": False},
    )
    expected_duration = timedelta(hours=1)
    assert (
        f"Max-Age={int(expected_duration.total_seconds())}"
        in response.headers["set-cookie"]
    )


@pytest.mark.anyio
async def test_unauthenticated_access(client):
    assert (await client.get("/user/me")).status_code == 401


@pytest.mark.anyio
async def test_token_expiration(client, test_user):
    expired_token = create_token(
        user_id=test_user["_id"], expiry_time=timedelta(seconds=-1), mode="user"
    )
    client.cookies.set("access_token", expired_token)
    assert (await client.get("/user/me")).status_code == 401


@pytest.mark.anyio
async def test_invalid_token(client):
    client.cookies.set("access_token", "not-a-valid-jwt")
    assert (await client.get("/user/me")).status_code == 401


@pytest.mark.anyio
async def test_logout(client, test_user):
    await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "test123"},
    )
    assert (await client.get("/user/me")).status_code == 200
    assert (await client.post("/auth/logout")).status_code == 200
    assert (await client.get("/user/me")).status_code == 401


@pytest.mark.anyio
async def test_admin_in_admin_mode(client, test_admin):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "test123", "mode": "admin"},
    )
    assert response.status_code == 200
    admin_response = await client.get("/admin/desks/")
    assert admin_response.status_code == 200


@pytest.mark.anyio
async def test_admin_in_user_mode(client, test_admin):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "test123", "mode": "user"},
    )
    assert response.status_code == 200
    assert (await client.get("/admin/desks/")).status_code == 403
    assert (await client.get("/user/me")).status_code == 200


@pytest.mark.anyio
async def test_user_in_admin_mode(client, test_user):
    response = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "test123", "mode": "admin"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_in_user_mode(client, test_user):
    response = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "test123", "mode": "user"},
    )
    assert response.status_code == 200
    assert (await client.get("/admin/desks/")).status_code == 403
    assert (await client.get("/user/me")).status_code == 200
