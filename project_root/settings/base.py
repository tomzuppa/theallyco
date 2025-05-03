"""
Base Django settings for the project.

This file contains shared settings used across environments.
Do not include environment-specific values here (e.g., DEBUG, DB credentials).
"""

from pathlib import Path
from decouple import config, Csv  # Load .env variables
from django.contrib.messages import constants as messages  # Import Django built-in message constants

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load secret key from environment
SECRET_KEY = config('SECRET_KEY')

# Debug is environment-specific (default is False)
DEBUG = False

# Allowed hosts will be set per environment
ALLOWED_HOSTS = []

# Core Django apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks', # Allows tweaking form field rendering attributes in templates (e.g., adding CSS classes).


    # Your custom apps go here
    'apps.users'  #login / logout

]

# Middleware settings (request/response lifecycle handlers)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'project_root.urls'

# Login no longer uses username, now handled via email through custom backend
AUTHENTICATION_BACKENDS = [
    'apps.users.authentication.EmailBackend',  # (login with email)
]


# Template engine settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global template directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project_root.settings.context_processors.current_year',  #assigning dinamically the current year (templates)

            ],
        },
    },
]

# WSGI application (used for deployments)
WSGI_APPLICATION = 'project_root.wsgi.application'

# Database settings will be defined per environment
DATABASES = {}

# Password validation rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]



"""
Django base settings configuration file.

This file includes all core settings such as localization, static and media files,
custom user models, authentication redirects, and trusted origins.
"""

# File: settings.py
# Purpose: Map Django message types to Bootstrap alert classes for consistent visual formatting across the platform.

# 🔥 Custom mapping for Django messages to Bootstrap classes
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',  # Debug messages will appear as Bootstrap 'secondary' (gray)
    messages.INFO: 'info',         # Info messages will appear as Bootstrap 'info' (blue)
    messages.SUCCESS: 'success',   # Success messages will appear as Bootstrap 'success' (green)
    messages.WARNING: 'warning',   # Warning messages will appear as Bootstrap 'warning' (yellow/orange)
    messages.ERROR: 'danger',      # Error messages will appear as Bootstrap 'danger' (red)
}

# 📋 This setting affects: 
# - Display of messages in templates (like base.html)
# - Visual color (class) assigned to each Django message
# - Ensures consistency between Django backend logic and Bootstrap frontend design



# -----------------------------------
# 🌐 Localization & Internationalization
# -----------------------------------
LANGUAGE_CODE = 'en-us'  # Default language code
TIME_ZONE = 'America/Mexico_City'  # Time zone for timestamps
USE_I18N = True  # Internationalization support
USE_TZ = True  # Timezone-aware datetime objects

# -----------------------------------
# 📁 Static Files (CSS, JS, Images)
# -----------------------------------
STATIC_URL = '/static/'  # URL path for static files
STATICFILES_DIRS = [BASE_DIR / 'static']  # Additional static files directories
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Collected static files location

# -----------------------------------
# 📂 Media Files (User Uploads)
# -----------------------------------
MEDIA_URL = '/media/'  # URL path for user-uploaded media files
MEDIA_ROOT = BASE_DIR / 'media'  # Physical location for storing uploaded files

# -----------------------------------
# 🔑 Custom User Model Configuration
# -----------------------------------
# Using a custom user model instead of Django's built-in model
AUTH_USER_MODEL = 'users.CustomUser'

# -----------------------------------
# 🌐 Root URL Configuration
# -----------------------------------
# Specifies the Python module containing the URL declarations
ROOT_URLCONF = 'project_root.urls'

# -----------------------------------
# 🛡️ Authentication and Redirection URLs
# -----------------------------------
# URL to redirect to for login if the user is not authenticated
LOGIN_URL = '/users/login/'

# URL to redirect users after successful login
LOGIN_REDIRECT_URL = '/users/dashboard/'  # 👈 Updated to modular path

# URL to redirect users after logout
LOGOUT_REDIRECT_URL = '/users/login/'


# -----------------------------------
# 🔒 Session Management Settings
# -----------------------------------

# Default session duration (only used if not overridden manually)
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1 day (in seconds)

# Do not expire session on browser close by default (we control it manually in views)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 🔥 Refresh session expiry on every request
# This allows implementing "auto-logout by inactivity" behavior
SESSION_SAVE_EVERY_REQUEST = True


# -----------------------------------
# 🔑 Security and Trusted Origins
# -----------------------------------
# Trusted origins for CSRF protection (update for production)
CSRF_TRUSTED_ORIGINS = [
    'https://8000-cs-61983882132-default.cs-us-central1-pits.cloudshell.dev',
    'https://8080-cs-61983882132-default.cs-us-central1-pits.cloudshell.dev',
]

# -----------------------------------
# ⚙️ Primary Key Field Type
# -----------------------------------
# Default primary key type for Django models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------------
# 🔐 reCAPTCHA keys loaded from .env file
# -----------------------------------
RECAPTCHA_SITE_KEY = config("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = config("RECAPTCHA_SECRET_KEY")
