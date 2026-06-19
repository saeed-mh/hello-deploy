from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_returns_hello_world() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello World" in response.text


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_endpoint() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_version_endpoint() -> None:
    response = client.get("/version")
    body = response.json()
    assert response.status_code == 200
    assert "version" in body
    assert "environment" in body
    assert "build_time" in body


def test_metrics_endpoint() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "hello_deploy_info" in response.text
