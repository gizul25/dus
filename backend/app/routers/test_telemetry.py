import pytest
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.mark.anyio
async def test_telemetry_ingest_minimal(client):
    response = await client.get("/telemetry/errors")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.post(
        "/telemetry/errors",
        json={"message": "boom"},
    )
    print(response.text)
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "received"
    assert isinstance(body["id"], str) and body["id"]

    response = await client.get("/telemetry/errors")
    assert response.status_code == 200
    errors = response.json()
    assert len(errors) == 1
    assert errors[0]["id"] == body["id"]
    assert errors[0]["message"] == "boom"
    assert errors[0]["source"] == "manual"
    assert errors[0]["received_at"] is not None


@pytest.mark.anyio
async def test_telemetry_ingest_full_payload(client):
    payload = {
        "message": "TypeError: x is undefined",
        "stack": "at foo (app.js:1)\nat bar (app.js:2)",
        "source": "window.error",
        "url": "http://app.io/some/page",
        "userAgent": "pytest-agent/1.0",
        "occurredAt": "2026-01-02T03:04:05Z",
        "context": {"route": "/desk", "attempt": 2},
    }
    response = await client.post("/telemetry/errors", json=payload)
    print(response.text)
    assert response.status_code == 202
    error_id = response.json()["id"]

    response = await client.get(f"/telemetry/errors/{error_id}")
    print(response.text)
    assert response.status_code == 200
    stored = response.json()
    assert stored["id"] == error_id
    assert stored["message"] == payload["message"]
    assert stored["stack"] == payload["stack"]
    assert stored["source"] == "window.error"
    assert stored["url"] == payload["url"]
    assert stored["user_agent"] == "pytest-agent/1.0"
    assert stored["context"] == payload["context"]
    assert stored["occurred_at"].startswith("2026-01-02T03:04:05")
    assert stored["received_at"] is not None


@pytest.mark.anyio
async def test_telemetry_ingest_defaults_source_to_manual(client):
    response = await client.post("/telemetry/errors", json={"message": "no source"})
    assert response.status_code == 202
    error_id = response.json()["id"]

    response = await client.get(f"/telemetry/errors/{error_id}")
    assert response.status_code == 200
    assert response.json()["source"] == "manual"


@pytest.mark.anyio
async def test_telemetry_ingest_falls_back_to_user_agent_header(client):
    response = await client.post(
        "/telemetry/errors",
        json={"message": "ua fallback"},
        headers={"User-Agent": "httpx-test/9.9"},
    )
    assert response.status_code == 202
    error_id = response.json()["id"]

    response = await client.get(f"/telemetry/errors/{error_id}")
    assert response.status_code == 200
    assert response.json()["user_agent"] == "httpx-test/9.9"


@pytest.mark.anyio
async def test_telemetry_ingest_invalid_empty_message(client):
    response = await client.post("/telemetry/errors", json={"message": ""})
    print(response.text)
    assert response.status_code == 422

    response = await client.post("/telemetry/errors", json={})
    print(response.text)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_telemetry_ingest_invalid_source(client):
    response = await client.post(
        "/telemetry/errors",
        json={"message": "x", "source": "not-a-real-source"},
    )
    print(response.text)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_telemetry_ingest_naive_timestamp_is_normalized(client):
    response = await client.post(
        "/telemetry/errors",
        json={"message": "naive ts", "occurredAt": "2026-05-06T07:08:09"},
    )
    print(response.text)
    assert response.status_code == 202
    error_id = response.json()["id"]

    response = await client.get(f"/telemetry/errors/{error_id}")
    assert response.status_code == 200
    assert response.json()["occurred_at"].startswith("2026-05-06T07:08:09")

@pytest.mark.anyio
async def test_telemetry_get_unknown_id(client):
    response = await client.get("/telemetry/errors/does-not-exist")
    print(response.text)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_telemetry_list_filter_by_source(client):
    sources = ["window.error", "window.error", "unhandledrejection", "manual"]
    for i, src in enumerate(sources):
        response = await client.post(
            "/telemetry/errors",
            json={"message": f"err-{i}", "source": src},
        )
        assert response.status_code == 202

    response = await client.get("/telemetry/errors")
    assert response.status_code == 200
    assert len(response.json()) == len(sources)

    response = await client.get("/telemetry/errors?source=window.error")
    print(response.text)
    assert response.status_code == 200
    filtered = response.json()
    assert len(filtered) == 2
    assert all(e["source"] == "window.error" for e in filtered)

    response = await client.get("/telemetry/errors?source=manual")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_telemetry_list_invalid_source_filter(client):
    response = await client.get("/telemetry/errors?source=bogus")
    print(response.text)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_telemetry_list_limit(client):
    for i in range(5):
        response = await client.post(
            "/telemetry/errors",
            json={"message": f"err-{i}"},
        )
        assert response.status_code == 202

    response = await client.get("/telemetry/errors?limit=2")
    print(response.text)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/telemetry/errors?limit=0")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/telemetry/errors?limit=10000")
    assert response.status_code == 200
    assert len(response.json()) == 5


@pytest.mark.anyio
async def test_telemetry_list_sorted_by_received_at_desc(client):
    ids = []
    for i in range(3):
        response = await client.post(
            "/telemetry/errors",
            json={"message": f"err-{i}"},
        )
        assert response.status_code == 202
        ids.append(response.json()["id"])

    response = await client.get("/telemetry/errors")
    assert response.status_code == 200
    got = [e["id"] for e in response.json()]

    assert got == list(reversed(ids))