# ✅ project_root/urls.py – Main URL Configuration
# --------------------------------------------------
# This file defines the global route mappings for the entire project.
# It handles:
# - Root redirection
# - Admin panel
# - OAuth2 callback
# - Delegation to app-level URL configs
# --------------------------------------------------

from django.contrib import admin                         # Django admin panel
from django.urls import path, include                    # URL routing utilities
from django.shortcuts import redirect                    # Utility for lambda redirection
from apps.users import views as user_views               # Google OAuth2 callback handler
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 🛠️ Django admin panel (accessed by superusers)
    path('admin/', admin.site.urls),

    # 🚪 Redirect root ("/") to the login page
    # 🔁 Improves UX by always routing root to a meaningful screen
    path('', lambda request: redirect('users:login')),

    # 👥 Load users app URL routes (login, register, dashboard, etc.)
    path('users/', include('apps.users.urls')),

    # 🔐 Google OAuth2 callback (receives response after Google login)
    # Must match Google's authorized redirect URI in GCP console
    path('oauth2callback/', user_views.oauth2callback, name='oauth2callback'),
]

# --------------------------------------------------
# 📦 MEDIA FILE HANDLER (Development Only)
# --------------------------------------------------
# This block enables Django to serve user-uploaded media files (e.g., images)
# during development via MEDIA_URL → MEDIA_ROOT mapping.

from django.conf import settings                   # 🔐 Access MEDIA_URL and MEDIA_ROOT from settings
from django.conf.urls.static import static         # 📦 Utility to serve media during development

# 🛠️ Only enable media serving if DEBUG is True (never use this in production!)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,                        # 📂 Example: "/media/"
        document_root=settings.MEDIA_ROOT          # 🗂️ Maps to the physical "media/" folder
    )
