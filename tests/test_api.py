import uuid
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from app.api import routes as routes_module
from app.db.deps import get_db
from app.db.models import Job
from app.main import create_app
from app.services.content_hash import compute_extracted_hash


class FakeDB:
    def __init__(self) -> None:
        self.jobs: dict[uuid.UUID, Job] = {}

    def add(self, job: Job) -> None:
        if getattr(job, "id", None) is None:
            job.id = uuid.uuid4()
        self.jobs[job.id] = job

    def commit(self) -> None:
        return None

    def refresh(self, job: Job) -> None:
        if getattr(job, "id", None) is None:
            job.id = uuid.uuid4()
        self.jobs[job.id] = job

    def get(self, model: type[Job], job_id: uuid.UUID) -> Optional[Job]:
        assert model is Job
        return self.jobs.get(job_id)


class FakeQueue:
    def __init__(self) -> None:
        self.items: list[str] = []

    def push(self, item: str) -> None:
        self.items.append(item)


class FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get_summary(self, content_hash: str) -> Optional[str]:
        return self.store.get(content_hash)

    def set_summary(self, content_hash: str, summary: str) -> None:
        self.store[content_hash] = summary


@pytest.fixture()
def client_and_fakes(monkeypatch: pytest.MonkeyPatch):
    fake_db = FakeDB()
    fake_queue = FakeQueue()
    fake_cache = FakeCache()

    def override_get_db():
        yield fake_db

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr(routes_module, "get_queue", lambda _url: fake_queue)
    monkeypatch.setattr(routes_module, "get_cache", lambda _url: fake_cache)

    client = TestClient(app)
    return client, fake_db, fake_queue, fake_cache


def test_submit_validation_both_url_and_text(client_and_fakes):
    client, _, _, _ = client_and_fakes
    r = client.post("/submit", json={"url": "https://example.com", "text": "x"})
    assert r.status_code == 400


def test_submit_validation_neither_url_nor_text(client_and_fakes):
    client, _, _, _ = client_and_fakes
    r = client.post("/submit", json={})
    assert r.status_code == 400


def test_submit_only_url_success(client_and_fakes):
    client, _, fake_queue, _ = client_and_fakes
    r = client.post("/submit", json={"url": "https://example.com"})
    assert r.status_code == 200
    body = r.json()
    assert "job_id" in body
    assert body["status"] == "queued"
    assert len(fake_queue.items) == 1


def test_submit_only_text_success(client_and_fakes):
    client, _, fake_queue, _ = client_and_fakes
    r = client.post("/submit", json={"text": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert "job_id" in body
    assert body["status"] == "queued"
    assert len(fake_queue.items) == 1


def test_status_unknown_job_id_404(client_and_fakes):
    client, _, _, _ = client_and_fakes
    r = client.get(f"/status/{uuid.uuid4()}")
    assert r.status_code == 404


def test_status_valid_job_id(client_and_fakes):
    client, fake_db, _, _ = client_and_fakes
    job = Job(status="queued", input_type="text", url=None, text="x", content_hash=compute_extracted_hash("x"))
    fake_db.add(job)
    r = client.get(f"/status/{job.id}")
    assert r.status_code == 200
    assert r.json()["status"] == "queued"


def test_result_not_completed_returns_null_summary(client_and_fakes):
    client, fake_db, _, _ = client_and_fakes
    job = Job(status="queued", input_type="text", url=None, text="x", content_hash=compute_extracted_hash("x"))
    fake_db.add(job)
    r = client.get(f"/result/{job.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["summary"] is None


def test_result_completed_returns_summary(client_and_fakes):
    client, fake_db, _, _ = client_and_fakes
    job = Job(
        status="completed",
        input_type="text",
        url=None,
        text="x",
        content_hash=compute_extracted_hash("x"),
        summary="done",
        cached=True,
        processing_time_ms=12,
    )
    fake_db.add(job)
    r = client.get(f"/result/{job.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["summary"] == "done"
    assert body["cached"] is True
    assert body["processing_time_ms"] == 12


def test_duplicate_text_cache_hit_optional(client_and_fakes):
    client, _, _, fake_cache = client_and_fakes
    h = compute_extracted_hash("dup")
    fake_cache.set_summary(h, "cached summary")
    r = client.post("/submit", json={"text": "dup"})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
