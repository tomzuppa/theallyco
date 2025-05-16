# 🔐 Custom Email Authentication Backend
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login using email + password.
    Does not handle 'is_verified' here; that is handled by the View layer for better user experience.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 🔍 Find the user by email instead of username
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None  # User does not exist

        # ✅ Validate password and let Django handle 'is_active'
        if user.check_password(password) and self.user_can_authenticate(user):
            return user  # Return the user if everything is OK

        return None  # Invalid credentials or inactive user