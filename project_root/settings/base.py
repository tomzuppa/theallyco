"""
Base Django settings for the project.

This file contains shared settings used across environments.
Do not include environment-specific values here (e.g., DEBUG, DB credentials).
"""

from pathlib import Path
from decouple import config, Csv  # Load .env variables

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

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static file settings (CSS, JS, images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🔐 Custom user model configuration
# This tells Django to use our CustomUser model instead of the default User
AUTH_USER_MODEL = 'users.CustomUser'

# Path to the root URL configuration file (urls.py)
# This tells Django which module contains the main URL declarations
ROOT_URLCONF = 'project_root.urls'

# 🔐 Default path to redirect after successful login
LOGIN_REDIRECT_URL = '/'

# 🔐 Default login view for @login_required decorators
LOGIN_URL = 'users:login'

LOGOUT_REDIRECT_URL = 'users:login'  # 🔄 Redirect to login after logout


# ----------------------------------------
# 🔐 Authentication Redirection Settings
# ----------------------------------------

# The URL where requests are redirected for login.
# This is used when the @login_required decorator is triggered
LOGIN_URL = '/users/login/'

# After a successful login, the user will be redirected to this URL.
# Typically used for dashboard or landing page after authentication
LOGIN_REDIRECT_URL = '/dashboard/'

# After logout, redirect the user to the login page
LOGOUT_REDIRECT_URL = '/users/login/'

# Server addres for GCP development environment (replace in production)
CSRF_TRUSTED_ORIGINS = [
    'https://8000-cs-61983882132-default.cs-us-central1-pits.cloudshell.dev',
]
