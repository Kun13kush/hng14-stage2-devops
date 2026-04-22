# Stage 1 — install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --prefix=/install

# Stage 2 — runtime
FROM python:3.12-slim
WORKDIR /app

# Patch OS-level packages (resolves OpenSSL CVEs)
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy installed packages and worker
COPY --from=builder /install /usr/local
COPY worker.py .

# Lock down ownership
RUN chown -R appuser:appgroup /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c \
    "import redis, os; redis.Redis(host=os.environ.get('REDIS_HOST','redis'), socket_connect_timeout=5).ping()" \
    || exit 1

CMD ["python", "worker.py"]