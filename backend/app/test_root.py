from fastapi import FastAPI
from fastapi.testclient import TestClient
from . import backend_app


client = TestClient(backend_app)

TOKEN = "jessica"

def _url(path: str) -> str:
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}token={TOKEN}"

def test_read_main():
    response = client.get(_url("/"))
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from backend!"}
