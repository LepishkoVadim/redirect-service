"""App config for the user management app."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Registers the ``apps.users`` application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"