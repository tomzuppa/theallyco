"""
Development settings for local use only.

This file extends base.py and enables features useful for debugging,
local testing, and non-production database connections.
"""

from .base import *  # Import all base settings

from decouple import config

# Enable Django's debug mode (do NOT use this in production!)
DEBUG = True

# Allow all hosts during local development
ALLOWED_HOSTS = ['*']

# SQLite database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Optional: Enable Django Debug Toolbar (if installed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
