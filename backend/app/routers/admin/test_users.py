import pytest
import logging
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient
import pymongo

from app import make_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

@pytest.mark.anyio
async def test_user_post(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.anyio
async def test_user_invalid_post(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/users/", json={
        "email": "bricky@supa.ch"
    })
    print(response.text)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_user_delete(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch"
    })
    print(response.text)
    assert response.status_code == 201
    assert response.json() == "123123123"

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.delete("/admin/users/123123123")
    print(response.text)
    assert response.status_code == 204

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_user_delete_fail(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.delete("/admin/users/123123123")
    print(response.text)
    assert response.status_code == 404

    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_user_put(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch"
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
        "email": "woody@supa.ch"
    })
    print(response.text)
    assert response.status_code == 200
    assert response.json()['first_name'] == "new woody"

@pytest.mark.anyio
async def test_user_put_fail(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "first_name": "woody",
        "last_name": "tree",
        "email": "woody@supa.ch"
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