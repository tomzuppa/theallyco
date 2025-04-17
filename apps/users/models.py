from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    You can add fields here like avatar, organization, etc.
    """
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True) #Upload the avatar image user
    is_verified = models.BooleanField(default=False)  # For email or 2FA logic in future
    # organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.SET_NULL)  # Optional for multitenancy

    def __str__(self):
        return self.username
