# ------------------------
# 🔐 Django AbstractUser for authentication extension
# ------------------------
from django.contrib.auth.models import AbstractUser  # Inherits Django's core user logic (username, password, groups, permissions, etc.)

# ------------------------
# 🧱 Django model base (ORM)
# ------------------------
from django.db import models


# ------------------------
# 👤 CustomUser model (extends AbstractUser)
# ------------------------
class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    🔐 Used as the main user class via AUTH_USER_MODEL in settings.py.

    ✅ Adds support for:
    - Email-based login
    - Google login integration
    - Profile picture
    - Account verification (2FA-like)
    - Extra profile fields (phone, country, postal code, language)

    Referenced in:
    - Login and registration views (views.py)
    - Forms like RegisterForm and EmailLoginForm (forms.py)
    - Token validation (activate_account)
    """

    # Email used as login credential (must be unique)
    email = models.EmailField(unique=True)

    # Optional profile picture (avatar)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Whether user verified their email address (via token)
    is_verified = models.BooleanField(default=False)

    # Optional contact fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    # Preferred language (used in i18n features)
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        default='en'
    )

    def __str__(self):
        """
        Returns the username for admin display and logging purposes.
        """
        return self.username


# ------------------------
# 🎛️ AuthConfig (admin-toggleable authentication settings)
# ------------------------
class AuthConfig(models.Model):
    """
    Centralized configuration model for toggling authentication options.

    💡 Used to:
    - Enable/disable the Google login button from the admin panel
    - Plan for future features like password reset toggle, 2FA enforcement, etc.

    Referenced in:
    - CustomLoginView → renders Google login button conditionally
    - Django admin → editable via UI
    """

    enable_google_login = models.BooleanField(
        default=False,
        help_text="Enable login with Google"
    )

    # Auto-updated timestamp for auditing
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Display label in Django admin panel.
        """
        return "Authentication Settings"
