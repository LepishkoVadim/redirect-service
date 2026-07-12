# syntax=docker/dockerfile:1

# --- Builder: resolve deps into a venv with uv -------------------------------
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY pyproject.toml uv.lock ./
# Runtime deps only (no dev group), no project install (bare project).
RUN uv sync --frozen --no-dev --no-install-project

# --- Runtime -----------------------------------------------------------------
FROM python:3.14-slim

RUN groupadd --system app && useradd --system --gid app --create-home app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . /app

RUN chmod +x /app/docker/*.sh && chown -R app:app /app

USER app
WORKDIR /app/src
EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
