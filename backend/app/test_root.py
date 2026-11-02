from fastapi import FastAPI
from fastapi.testclient import TestClient
from . import backend_app


client = TestClient(backend_app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from backend!"}
