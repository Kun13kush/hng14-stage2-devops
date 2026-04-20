from main import app
import main
from fastapi.testclient import TestClient
import fakeredis
import os

os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("QUEUE_NAME", "jobs_queue")
os.environ.setdefault("JOB_EXPIRE_SECONDS", "86400")


fake = fakeredis.FakeRedis()


def override_get_redis():
    return fake


app.dependency_overrides[main.get_redis] = override_get_redis

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job():
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


def test_get_job_status():
    create = client.post("/jobs")
    job_id = create.json()["job_id"]
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_get_unknown_job():
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404


def test_job_added_to_queue():
    queue_name = os.environ.get("QUEUE_NAME", "jobs_queue")
    before = fake.llen(queue_name)
    client.post("/jobs")
    after = fake.llen(queue_name)
    assert after == before + 1
