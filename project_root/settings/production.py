"""
Production settings for deployment.

These settings should never expose sensitive debug tools or allow unrestricted access.
Values are pulled from environment variables to enhance security and flexibility.
"""

from .base import *  # Import everything from base settings
from decouple import config, Csv

# In production, DEBUG must always be False
DEBUG = False

# Define specific allowed hosts (e.g., domain or server IP)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Production database settings (e.g., PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}

# Recommended: enable secure settings (optional at this stage)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
