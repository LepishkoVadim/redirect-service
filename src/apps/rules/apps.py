"""App config for the URL management app."""

from django.apps import AppConfig


class RulesConfig(AppConfig):
    """Registers the ``apps.rules`` application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rules"