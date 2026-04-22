# Stage 1 — install dependencies
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --prefix=/install

# Stage 2 — runtime
FROM python:3.12-slim-bookworm
WORKDIR /app

# Patch OS-level packages (resolves OpenSSL and other CVEs)
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy dependencies and application code only
COPY --from=builder /install /usr/local
COPY main.py .
# Add other specific files rather than COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--no-access-log"]