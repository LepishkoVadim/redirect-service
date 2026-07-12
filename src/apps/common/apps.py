"""App config for the shared ``common`` app."""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Registers the ``apps.common`` application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
