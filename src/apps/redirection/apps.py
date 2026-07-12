"""App config for the redirect module."""

from django.apps import AppConfig


class RedirectionConfig(AppConfig):
    """Registers the ``apps.redirection`` application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.redirection"