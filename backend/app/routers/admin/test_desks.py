import os
import pytest
import logging
from argon2 import PasswordHasher
from pymongo import MongoClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

@pytest.fixture
def db():
    with MongoClient(os.environ["MONGODB_URL"]) as mongo:
        yield mongo["testdb"]

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
async def test_login_as_admin(client, test_admin):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "test123", "mode": "admin"},
    )
    assert response.status_code == 200
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_desk_post(client, test_admin):
    await test_login_as_admin(client, test_admin)
    response = await client.post("/admin/desks/", json={
        "_id": "123123123",
        "name": "desk1",
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.anyio
async def test_desk_invalid_post(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/desks/", json={
        "_id": "123123123"
    })
    print(response.text)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_desk_invalid_post_empty(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/desks/", json={})
    print(response.text)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_desk_delete(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/desks/", json={
        "_id": "123123123",
        "name": "woody"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.delete("/admin/desks/123123123")
    print(response.text)
    assert response.status_code == 204

    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_desk_delete_fail(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.delete("/admin/desks/123123123")
    print(response.text)
    assert response.status_code == 404

    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_desk_put(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/desks/", json={
        "_id": "123123123",
        "name": "desk1",
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/desks/123123123")
    assert response.status_code == 200
    assert response.json()['name'] == 'desk1'

    response = await client.put("/admin/desks/123123123", json={
        "name": "desknew",
    })
    print(response.text)
    assert response.status_code == 200
    assert response.json()['name'] == "desknew"

@pytest.mark.anyio
async def test_desk_put_fail(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/desks/", json={
        "_id": "123123123",
        "name": "desk1",
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/desks/123123123")
    assert response.status_code == 200
    assert response.json()['name'] == 'desk1'

    response = await client.put("/admin/desks/123123123", json={})
    print(response.text)
    assert response.status_code == 422

    response = await client.get("/admin/desks/123123123")
    assert response.status_code == 200
    assert response.json()['name'] == 'desk1'