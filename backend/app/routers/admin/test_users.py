from contextlib import asynccontextmanager
import os
from asgi_lifespan import LifespanManager
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

@pytest.fixture
async def app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info('lifespan starting')

        app.mongo_client = pymongo.MongoClient(os.environ["MONGODB_URL"])
        db_name = "testdb"
        app.mongo_client.drop_database(db_name)
        app.db = app.mongo_client[db_name]

        logger.info('lifespan ready')

        yield

        logger.info('lifespan closing')

        app.mongo_client.close()
        app.mongo_client = None
        app.db = None

        logger.info('lifespan closed')

    app = make_app(lifespan)

    async with LifespanManager(app) as manager:
        print("We're in!")
        yield manager.app
        

@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://app.io"
    ) as client:
        print("Client is ready")
        yield client

@pytest.mark.anyio
async def test_user_post(client):
    response = await client.get("/admin/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post("/admin/users/", json={
        "_id": "123123123",
        "name": "woody",
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
        "name": "woody",
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

# TODO: add more tests
# TODO: migrate test fixtures to lib
# TODO: update test_root.py to use standard async testing