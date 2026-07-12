#!/usr/bin/env bash
# Dev entrypoint: ensure logs dir → wait for DB → migrate → runserver (autoreload).
# No collectstatic/gunicorn — DEBUG serves static and runserver reloads on file change.
set -euo pipefail

: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"

# Absolute path = the mounted logs volume (app-writable). CWD is /app/src, which the dev
# bind-mount makes host-owned, so a relative "logs" mkdir there would fail.
mkdir -p /app/logs

echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
until python -c "import socket,sys; s=socket.socket(); s.settimeout(2); \
sys.exit(0) if s.connect_ex(('${POSTGRES_HOST}', ${POSTGRES_PORT}))==0 else sys.exit(1)"; do
  sleep 1
done
echo "Postgres is up."

python manage.py migrate --noinput

# Optional superuser bootstrap (no-op if username unset or already exists).
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  python manage.py createsuperuser --noinput || true
fi

exec python manage.py runserver 0.0.0.0:8000
