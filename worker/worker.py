import redis
import time
import os
import signal

def get_redis():
    while True:
        try:
            client = redis.Redis(
                host=os.environ.get("REDIS_HOST", "redis"),
                port=int(os.environ.get("REDIS_PORT", 6379))
            )
            client.ping()
            return client
        except redis.ConnectionError:
            print("Redis not ready, retrying in 2s...")
            time.sleep(2)

r = get_redis()
queue_name = os.environ.get("QUEUE_NAME", "jobs_queue")

def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

def handle_shutdown(signum, frame):
    print("Shutting down worker...")
    exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

while True:
    job = r.brpop(queue_name, timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())