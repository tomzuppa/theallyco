# 🔐 Custom Email Authentication Backend
# --------------------------------------------------
# Enables user authentication via email instead of username
# Used in: CustomLoginView (views.py)
# Defined in: apps/users/authentication.py (recommended location)
# --------------------------------------------------

from django.contrib.auth.backends import ModelBackend  # 🔧 Base backend for default authentication logic
from django.contrib.auth import get_user_model         # 🔁 Dynamic import of the correct User model

# 📦 Loads the active custom user model (AUTH_USER_MODEL from settings.py)
UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """
    📨 Custom authentication backend that enables email + password login.

    ✨ Key points:
    - Overrides `authenticate()` method
    - Matches email instead of username
    - Lets Django handle password check and active status

    ⚠️ `is_verified` is NOT checked here, to allow fine-grained control from views.

    Referenced in:
    - settings.py → AUTHENTICATION_BACKENDS
    - views.CustomLoginView (calls login(..., backend='apps.users.authentication.EmailBackend'))
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 🔍 Search user by email (instead of username)
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None  # ⛔ No such email registered

        # 🔐 Validate password and check if user is allowed to authenticate
        if user.check_password(password) and self.user_can_authenticate(user):
            return user  # ✅ Successful authentication

        return None  # ⛔ Invalid credentials or user is inactive
