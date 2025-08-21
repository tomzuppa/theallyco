# ------------------------
# 🔔 signals.py - Auto-create user profiles based on user_type
# ------------------------

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import CustomUser, EmployeeProfile, ClientProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a related profile when a new user is created.
    
    🔄 Logic:
    - If user_type == 'employee' → Create EmployeeProfile
    - If user_type == 'client' → Create ClientProfile
    """

    if created:
        if instance.user_type == 'employee':
            EmployeeProfile.objects.create(user=instance)
        elif instance.user_type == 'client':
            ClientProfile.objects.create(user=instance)
