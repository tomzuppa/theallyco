# ⚙️ Django application configuration for the 'users' app
from django.apps import AppConfig


class UsersConfig(AppConfig):
    # 🧱 Sets the default type for primary keys across models in this app
    # Impacts: Ensures all models in this app use BigAutoField unless otherwise specified
    default_auto_field = 'django.db.models.BigAutoField'

    # 🗂️ Defines the dotted path to the app — important for app registry and template resolution
    # Impacts: Required for Django to correctly locate templates, static files, and models in 'apps.users'
    name = 'apps.users'
