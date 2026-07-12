"""Admin registration for the custom user model (the only way users are created)."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User

admin.site.register(User, UserAdmin)