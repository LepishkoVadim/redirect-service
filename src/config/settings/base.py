"""Shared Django settings for every environment.

Values that differ per environment (DEBUG, security, throttle rates) are read from
the environment via ``django-environ`` or overridden in ``local.py`` / ``production.py``.
"""

from datetime import timedelta
from pathlib import Path

import environ

from config.logging import build_logging_config

# src/config/settings/base.py → parents: [0]=settings [1]=config [2]=src [3]=repo root
SRC_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = SRC_DIR.parent

env = environ.Env()
# Load .env if present. read_env does NOT override variables already in the real environment,
# so compose/CI `environment:` values take precedence over the .env file.
environ.Env.read_env(ROOT_DIR / ".env")

# --- Core -------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
# Origins trusted for unsafe (POST) requests from the admin / browsable API. List every
# scheme+host the app is served on, e.g. "https://redirect-service.pp.ua" (live domain) or
# "http://<elastic-ip>" (a fresh Terraform box before TLS). Empty by default.
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Applications -----------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_structlog",
]
LOCAL_APPS = [
    "apps.common",
    "apps.users",
    "apps.rules",
    "apps.redirection",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Project owns its user table from day one (see apps.users.models.User).
AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Binds request_id + user_id onto every downstream log line.
    "django_structlog.middlewares.RequestMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Database (PostgreSQL) --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="redirect"),
        "USER": env("POSTGRES_USER", default="redirect"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="redirect"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}

# --- Cache (Redis) — also backs DRF throttling counters ---------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# --- Auth / password validation ---------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- I18N / TZ --------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static -----------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = ROOT_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- Django REST Framework --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.DefaultPagination",
    "PAGE_SIZE": 25,
    # Opt-in per public view; global default is unthrottled (private + CRUD stay unlimited).
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "public_redirect": env("THROTTLE_PUBLIC_REDIRECT", default="60/min"),
        "token": env("THROTTLE_TOKEN", default="10/min"),
    },
    "EXCEPTION_HANDLER": "apps.common.exceptions.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Number of proxies (nginx) in front, so throttling reads the real client IP from
    # X-Forwarded-For instead of the proxy's address. 0 when running without a proxy.
    "NUM_PROXIES": env.int("DJANGO_NUM_PROXIES", default=0),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Redirect Service API",
    "DESCRIPTION": "Manage public/private redirect rules and resolve redirects.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# --- JWT (SimpleJWT) --------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_LIFETIME_MIN", default=5)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_LIFETIME_DAYS", default=1)),
    # Rotate on refresh and blacklist the used token so a leaked refresh can't be replayed.
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer", "Token"),
}

# --- Logging ----------------------------------------------------------------
LOG_DIR = ROOT_DIR / env("DJANGO_LOG_DIR", default="logs")
LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="INFO")
LOGGING = build_logging_config(log_dir=LOG_DIR, level=LOG_LEVEL)
