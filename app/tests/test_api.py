import pytest
from fastapi.testclient import TestClient

from app.api import app, received_metrics

client = TestClient(app)

PAYLOAD = {
    "agent": "system-metrics-agent",
    "event_type": "system_metrics",
    "data": {"hostname": "test"},
}


@pytest.fixture(autouse=True)
def clean_state():
    received_metrics.clear()
    yield
    received_metrics.clear()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_metrics_created():
    response = client.post("/metrics", json=PAYLOAD)

    assert response.status_code == 201
    assert response.json()["total_received"] == 1


def test_post_metrics_invalid_payload():
    response = client.post("/metrics", json={"agent": ""})

    assert response.status_code == 422


def test_get_metrics_returns_all():
    client.post("/metrics", json=PAYLOAD)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_latest_metrics_not_found():
    response = client.get("/metrics/latest")

    assert response.status_code == 404


def test_latest_metrics_returns_last():
    client.post("/metrics", json=PAYLOAD)

    response = client.get("/metrics/latest")

    assert response.status_code == 200
    assert response.json()["agent"] == "system-metrics-agent"
