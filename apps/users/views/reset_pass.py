# ---------------------------------------------
# ✅ Custom Password Reset View
# Handles password reset via email + reCAPTCHA + logging
# ---------------------------------------------

# 🌐 Django built-in imports
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from core.utils import get_device_info

# 🧠 Custom utilities
from core.utils import get_client_ip, get_user_agent, validate_recaptcha

# 📝 Logging model for password reset attempts
from apps.users.models import PasswordResetLog

# 📄 Custom password reset form with email context override
from apps.users.forms import CustomPasswordResetForm 

# 💬 Centralized system messages
from project_root import messages as sysmsg  # Asegúrate de que este import ya existe


class CustomPasswordResetView(PasswordResetView):
    """
    📤 Handles password reset requests via email.

    Key features:
    - Validates Google reCAPTCHA
    - Logs every attempt with IP + user agent
    - Blocks excessive attempts to prevent abuse
    - Injects correct domain for Cloud email links
    - Uses custom dark mode template for reset form
    """

    # 🌌 HTML template shown to the user for entering email
    template_name = 'users/password_reset.html'

    # 📧 Email content sent to user with reset link
    email_template_name = 'emails/password_reset_email.html'

    # ✅ Redirect here after successfully submitting email form
    success_url = reverse_lazy('users:password_reset_done')

    subject_template_name = 'emails/password_reset_subject.txt'

    # 📄 Use custom form to inject Cloud domain into email context
    form_class = CustomPasswordResetForm 

    # ⏱️ Attempt limits (to avoid abuse)
    MAX_ATTEMPTS = 3
    BLOCK_WINDOW_MINUTES = 15

    # ---------------------------------------------
    # 🔐 Inject reCAPTCHA key into template context
    # ---------------------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RECAPTCHA_SITE_KEY'] = settings.RECAPTCHA_SITE_KEY
        return context

    # ---------------------------------------------
    # 🌐 Inject correct domain + protocol in email context
    # ---------------------------------------------
    def get_email_context(self, context):
        context = super().get_email_context(context)
        context["domain"] = settings.SITE_DOMAIN.replace("https://", "").replace("http://", "")
        context["protocol"] = "https"
        return context

    # ---------------------------------------------
    # ✅ Handle form submission: validate reCAPTCHA + limit attempts + log
    # ---------------------------------------------
    def form_valid(self, form):
        # ⛔ CAPTCHA check
        if not validate_recaptcha(self.request):
            return self.form_invalid(form)

        # 📌 Extract info from form + request
        email = form.cleaned_data.get('email')
        ip = get_client_ip(self.request)
        agent = get_user_agent(self.request)
        device_data = get_device_info(agent)

        # 🚫 Check recent attempts for this email
        window_start = timezone.now() - timedelta(minutes=self.BLOCK_WINDOW_MINUTES)
        recent_attempts = PasswordResetLog.objects.filter(
            email=email,
            timestamp__gte=window_start
        ).count()

        if recent_attempts >= self.MAX_ATTEMPTS:
            messages.error(self.request, sysmsg.MESSAGES["RESEND_LIMIT_EXCEEDED"])
            return self.form_invalid(form)

        # 📝 Save log of this reset request (successful = False by default)
        PasswordResetLog.objects.create(
            email=email,
            successful=False,
            ip_address=ip,
            user_agent=agent,
            device_type=device_data["device_type"],
            browser=device_data["browser"],
            os=device_data["os"]            
        )

        # ✅ Continue standard reset flow
        return super().form_valid(form)
