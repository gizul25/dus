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
async def test_desk_post(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

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
async def test_desk_invalid_post(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/desks/", json={
        "_id": "123123123"
    })
    print(response.text)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_desk_invalid_post_empty(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/desks/", json={})
    print(response.text)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_desk_delete(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

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
async def test_desk_delete_fail(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.delete("/admin/desks/123123123")
    print(response.text)
    assert response.status_code == 404

    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_desk_put(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

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
async def test_desk_put_fail(client):
    response = await client.get("/admin/desks/")
    assert response.status_code == 200
    assert response.json() == []

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