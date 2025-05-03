from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds additional fields for profile management.
    """
    # ✅ Required to login with email
    email = models.EmailField(unique=True)  

    # 🖼️ Optional avatar image
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # ✅ For email verification, 2FA logic, etc.
    is_verified = models.BooleanField(default=False)

    # ☎️ Contact number
    phone = models.CharField(max_length=20, blank=True, null=True)

    # 🌍 User's country
    country = models.CharField(max_length=50, blank=True, null=True)

    # 🏤 Postal code (for address info)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    # 🌐 Language preference (for localization)
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        default='en'
    )

    def __str__(self):
        return self.username
