# 🔐 Imports Django's abstract base user class to extend authentication logic
# Impacts: CustomUser inherits username, password, groups, permissions, and auth methods
from django.contrib.auth.models import AbstractUser

# 🧱 Django ORM tools for defining database models
# Impacts: Enables defining fields like CharField, BooleanField, DateTimeField, etc.
from django.db import models


class CustomUser(AbstractUser):
    """
    👤 Custom user model extending Django's AbstractUser base class.

    Impacts:
    - Used across the platform as the primary user model (AUTH_USER_MODEL)
    - Supports email login, Google login, and extended profile fields
    - Integrated into all authentication views and registration forms
    """

    # 📧 Primary login identifier (required for custom authentication and OAuth2)
    email = models.EmailField(unique=True)

    # 🖼️ Optional profile picture (used in user profile and dashboard UI)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # 🔐 Email verification status (used for 2FA, restricted access, etc.)
    is_verified = models.BooleanField(default=False)

    # ☎️ User's contact number (optional, for profile or notifications)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # 🌍 Country field for user segmentation or localization
    country = models.CharField(max_length=50, blank=True, null=True)

    # 🏤 Postal code for geographic segmentation or address data
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    # 🌐 Preferred language for multilingual platform support
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        default='en'
    )

    def __str__(self):
        # Impacts: Displayed in admin and logging/debugging tools
        return self.username



"""-----------------------------------------------------------------------
ENABLE O DISABLE GOOGLE LOGIN BUTTON IN THE LOGIN PAGE FROM ADMIN PANEL
-------------------------------------------------------------------------"""

class AuthConfig(models.Model):
    """
    🎛️ Centralized authentication configuration model.

    Impacts:
    - Enables or disables the Google login button dynamically from the admin panel
    - Used in CustomLoginView to conditionally render the button
    - Supports future expansion for global auth-related flags (e.g., 2FA, password reset toggle, etc.)
    """

    enable_google_login = models.BooleanField(
        default=False,
        help_text="Enable login with Google"
    )

    # 📅 Tracks last update timestamp for auditing changes to authentication settings
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Impacts: Label used in Django admin interface for this singleton config
        return "Authentication Settings"
