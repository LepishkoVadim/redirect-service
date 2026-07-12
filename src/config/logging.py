"""Logging configuration: structlog console + multi-process-safe rotating JSON files.

Every request carries a ``request_id`` (bound by ``django_structlog``); app modules log
via ``structlog.get_logger(__name__)``. File handlers use ``ConcurrentRotatingFileHandler``
so rotation stays safe when gunicorn runs multiple workers.
"""

from pathlib import Path
from typing import Any

import structlog

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
_BACKUP_COUNT = 5

# Shared structlog pre-processing applied before handing off to stdlib logging.
_PRE_CHAIN = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def configure_structlog() -> None:
    """Wire structlog to route records through stdlib logging (called from base settings)."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def build_logging_config(*, log_dir: Path, level: str) -> dict[str, Any]:
    """Build the Django ``LOGGING`` dict.

    Args:
        log_dir: Directory that receives the rotating log files (created if missing).
        level: Root log level, e.g. ``"INFO"`` (from ``DJANGO_LOG_LEVEL``).

    Returns:
        A ``logging.config.dictConfig``-compatible mapping.
    """
    configure_structlog()
    log_dir.mkdir(parents=True, exist_ok=True)

    def _file(name: str, file_level: str) -> dict[str, Any]:
        return {
            "level": file_level,
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "filename": str(log_dir / name),
            "maxBytes": _MAX_BYTES,
            "backupCount": _BACKUP_COUNT,
            "formatter": "json",
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # Human-readable, colored key=value for the console (dev).
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": _PRE_CHAIN,
            },
            # Machine-parseable JSON for files.
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": _PRE_CHAIN,
            },
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "console"},
            "app_file": _file("app.log", level),
            "error_file": _file("error.log", "ERROR"),
            "security_file": _file("security.log", "INFO"),
        },
        "loggers": {
            "django": {"handlers": ["console", "app_file", "error_file"], "level": level},
            "django.security": {
                "handlers": ["security_file"],
                "level": "INFO",
                "propagate": False,
            },
            # SQL echo only when explicitly debugging; off by default.
            "django.db.backends": {"handlers": ["console"], "level": "WARNING", "propagate": False},
            "django_structlog": {"handlers": ["console", "app_file"], "level": level},
            "apps": {"handlers": ["console", "app_file", "error_file"], "level": level},
        },
        "root": {"handlers": ["console", "app_file", "error_file"], "level": level},
    }
