import os
import pytest
from argon2 import PasswordHasher
from pymongo import MongoClient


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
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == [{'_id': 'test-admin', 'first_name': 'Testing', 'last_name': 'Admin', 'email': 'admin@example.com', 'role': 'admin'}]

@pytest.mark.anyio
async def test_user_post(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch",
        "password": PasswordHasher().hash("password"),
        "role": "user"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2 

@pytest.mark.anyio
async def test_user_invalid_post(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/users/", json={
        "email": "bricky@supa.ch"
    })
    print(response.text)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_user_delete(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch",
        "password": PasswordHasher().hash("password"),
        "role": "user"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.delete("/admin/users/123123123")
    print(response.text)
    assert response.status_code == 204

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == [{'_id': 'test-admin', 'first_name': 'Testing', 'last_name': 'Admin', 'email': 'admin@example.com', 'role': 'admin'}]

@pytest.mark.anyio
async def test_user_delete_fail(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.delete("/admin/users/123123123")
    print(response.text)
    assert response.status_code == 404

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == [{'_id': 'test-admin', 'first_name': 'Testing', 'last_name': 'Admin', 'email': 'admin@example.com', 'role': 'admin'}]

@pytest.mark.anyio
async def test_user_put(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch",
        "password": PasswordHasher().hash("password"),
        "role": "user"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/users/123123123")
    assert response.status_code == 200
    assert response.json()['first_name'] == 'woody'

    response = await client.put("/admin/users/123123123", json={
        "first_name": "new woody",
        "last_name": "tree",
        "email": "woody@supa.ch",
        "password": PasswordHasher().hash("password"),
        "role": "user"
    })
    print(response.text)
    assert response.status_code == 200
    assert response.json()['first_name'] == "new woody"

@pytest.mark.anyio
async def test_user_put_fail(client, test_admin):
    await test_login_as_admin(client, test_admin)

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch",
        "password": PasswordHasher().hash("password"),
        "role": "user"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/users/123123123")
    assert response.status_code == 200
    assert response.json()['first_name'] == 'woody'

    response = await client.put("/admin/users/123123123", json={})
    print(response.text)
    assert response.status_code == 422

    response = await client.get("/admin/users/123123123")
    assert response.status_code == 200
    assert response.json()['first_name'] == 'woody'