from typing import Generator
import os
import sys

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from main import app
from tasks import celery_app


@pytest.fixture(autouse=True)
def celery_eager() -> Generator[None, None, None]:
    """
    Run Celery tasks eagerly (synchronously) during tests.

    This makes tests fast and removes the need for a running worker/broker.
    """
    previous_always_eager = celery_app.conf.task_always_eager
    previous_propagates = celery_app.conf.task_eager_propagates
    previous_store_result = getattr(celery_app.conf, "task_store_eager_result", False)

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    celery_app.conf.task_store_eager_result = True

    try:
        yield
    finally:
        celery_app.conf.task_always_eager = previous_always_eager
        celery_app.conf.task_eager_propagates = previous_propagates
        celery_app.conf.task_store_eager_result = previous_store_result


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_submit_and_result_success(client: TestClient) -> None:
    response = client.post("/submit", json={"n": 5})
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data

    request_id = data["request_id"]

    result_resp = client.get(f"/result/{request_id}")
    assert result_resp.status_code == 200
    result_data = result_resp.json()

    assert result_data["status"] == "SUCCESS"
    assert result_data["result"] == [2, 3, 5, 7, 11]


def test_submit_validation(client: TestClient) -> None:
    response = client.post("/submit", json={"n": 0})
    assert response.status_code == 422


def test_worker_status_healthy(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    def fake_ping(timeout: float = 1.0):  # type: ignore[override]
        return [{"worker@local": "pong"}]

    monkeypatch.setattr(celery_app.control, "ping", fake_ping)

    resp = client.get("/worker-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["healthy"] is True
    assert data["workers"] == [{"worker@local": "pong"}]


