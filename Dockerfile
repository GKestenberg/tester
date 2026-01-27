FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY hello_world.py .
COPY hello_crash.py .
COPY hello_sigterm.py .
COPY hello_fail_health.py .
COPY gpu.py .
COPY aws_iam.py .
COPY metrics.py .
COPY temporal_worker.py .
COPY temporal_client.py .
COPY gpu_burner.py .
COPY health.py .

RUN uv sync --no-dev

EXPOSE 8000
