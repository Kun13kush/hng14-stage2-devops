# Stage 1 — install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --target=/install

# Stage 2 — runtime
FROM python:3.12-slim
WORKDIR /app

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy installed packages and worker file
COPY --from=builder /install /usr/local/lib/python3.12/site-packages
COPY worker.py .

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import redis, os; r=redis.Redis(host=os.environ.get('REDIS_HOST','redis')); r.ping()" || exit 1

CMD ["python", "worker.py"]
