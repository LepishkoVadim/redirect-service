"""Gunicorn configuration for the web service."""

import os

# Bind inside the container; nginx/host maps the port.
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.environ.get("GUNICORN_WORKERS", "3"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "30"))
wsgi_app = "config.wsgi:application"
accesslog = "-"  # stdout; structlog/console handler formats it
errorlog = "-"
# Trust the X-Forwarded-* headers set by the nginx reverse proxy.
forwarded_allow_ips = os.environ.get("GUNICORN_FORWARDED_ALLOW_IPS", "*")
