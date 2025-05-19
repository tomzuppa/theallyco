# ✅ project_root/wsgi.py – Cleaned and Explained
# --------------------------------------------------
# WSGI (Web Server Gateway Interface) entry point for deployment
# Used by production-grade web servers (Gunicorn, uWSGI, etc.) to serve the Django app
# --------------------------------------------------

import os
from django.core.wsgi import get_wsgi_application

# 🌍 Sets the default Django settings module for the WSGI environment
# 🔁 Can be swapped depending on deployment environment (e.g. production, staging)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.development')

# 🚀 WSGI application object used by WSGI-compatible servers (Gunicorn, etc.)
# This exposes the `application` callable Django needs to start serving requests
application = get_wsgi_application()

"""
🔧 Deployment Notes:
- WSGI is the standard Python interface between web servers and web applications.
- This file is typically used in production (e.g., with Gunicorn, mod_wsgi)
- For local development, Django uses ASGI (runserver → asgi.py)

🧪 For ASGI-based projects (async-ready), use asgi.py instead of wsgi.py
"""
