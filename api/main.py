from fastapi import FastAPI, HTTPException, Depends
import redis
import uuid
import os

app = FastAPI()

redis_pool = None


def get_redis():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool(
            host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", 6379))
        )
    return redis.Redis(connection_pool=redis_pool)


@app.post("/jobs")
def create_job(r=Depends(get_redis)):
    job_id = str(uuid.uuid4())
    queue_name = os.environ.get("QUEUE_NAME", "jobs_queue")
    r.hset(f"job:{job_id}", mapping={"status": "queued"})
    r.expire(f"job:{job_id}", int(os.environ.get("JOB_EXPIRE_SECONDS", 86400)))
    r.lpush(queue_name, job_id)
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str, r=Depends(get_redis)):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    if isinstance(status, bytes):
        status = status.decode()
    return {"job_id": job_id, "status": status}


@app.get("/health")
def health():
    return {"status": "ok"}
