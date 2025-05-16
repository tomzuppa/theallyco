# 🔧 Django admin interface for managing database models
from django.contrib import admin

# 🛣️ Core tools for URL routing in Django
from django.urls import path, include

# 🔁 Redirect utility for handling simple redirects (used for root URL)
from django.shortcuts import redirect

# 👤 Custom views from users app (used for Google OAuth callback)
from apps.users import views as user_views  # helpful for google login


urlpatterns = [
    # 🛠️ Django admin panel (default route for superusers)
    path('admin/', admin.site.urls),

    # 🚪 Redirect root URL "/" to the login page
    # Impacts: Ensures users land on login instead of a blank or 404 page
    path('', lambda request: redirect('users:login')),

    # 👥 Include all URL patterns from the users app (login, logout, register, dashboard, etc.)
    path('users/', include('apps.users.urls')),

    # 🔄 Google OAuth2 callback route
    # Impacts: This is the endpoint Google redirects to after user login
    # Must match the value defined in your Google OAuth app → Authorized Redirect URIs
    path('oauth2callback/', user_views.oauth2callback, name='oauth2callback'),
]
