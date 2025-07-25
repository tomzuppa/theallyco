# 🔐 Handles the password reset link and sets new password
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from apps.users.models import PasswordResetLog
from django.contrib.auth.views import PasswordResetCompleteView
from project_root import messages as sysmsg  # ✅ Custom messages

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    ✅ Handles the password reset link from the email.

    Features:
    - Validates the token from the email
    - Shows the form to set a new password
    - Updates PasswordResetLog as successful
    - Uses custom dark mode template
    """

    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

    def form_valid(self, form):
        # ✅ Get the user from the resolved token
        user = self.user
        email = user.email

        # 🧼 Mark all reset attempts as successful
        PasswordResetLog.objects.filter(email=email, successful=False).update(successful=True)

        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
    success_url = reverse_lazy('users:login')  # redirect to login

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_password_changed"] = sysmsg.MESSAGES["PASSWORD_CHANGED"]
        return context
