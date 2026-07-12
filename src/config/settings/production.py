"""Production settings.

DEBUG off, fail-fast on missing secrets, TLS/HSTS hardening, and persistent DB connections.
Secure by default: served behind nginx + Let's Encrypt (prod + tls compose overlays). The
SSL-redirect / HSTS / secure-cookie flags stay env-overridable but default to the safe values.
"""

from .base import *  # noqa: F401,F403
from .base import DATABASES, env

DEBUG = False

# Fail fast: no insecure fallbacks in production. Both are always provided by the
# deployment (.env written by Terraform / compose env) — a missing value should crash
# at boot, not silently run with a dev key or empty host list.
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# Persistent DB connections: reuse for up to 60s instead of reconnecting per request,
# with a liveness check so a recycled Postgres doesn't surface as request errors.
DATABASES["default"]["CONN_MAX_AGE"] = 60
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# TLS is mandatory — JWT travels in the Authorization header.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Container healthchecks hit /health/ over plain HTTP inside the network — exempt it
# from the HTTPS redirect (everything else still redirects).
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# HTTPS-only cookies (the app always sits behind TLS in production).
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
