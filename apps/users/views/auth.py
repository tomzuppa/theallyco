# -----------------------------------------
# 🔐 AUTHENTICATION VIEWS: Login & Logout
# -----------------------------------------

# 📦 Django Core & Auth Modules
from django.shortcuts import redirect            # Used to redirect users after logout
from django.urls import reverse_lazy             # Used for lazy URL resolution in class-based views
from django.contrib.auth import login, logout    # Django session-based login/logout functions
from django.contrib.auth.views import LoginView  # Base LoginView to extend
from django.contrib import messages              # Django flash message system
from django.conf import settings                 # Project settings (used for reCAPTCHA)
from project_root import messages as sysmsg      # Custom system messages from central file

# 🧠 Custom Forms and Models
from apps.users.forms import EmailLoginForm     # Custom form using email + password
from apps.users.models import AuthConfig        # DB toggle for showing Google login button

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ⚠️ DEV ONLY: Allows OAuth2 over HTTP

class CustomLoginView(LoginView):
    """
    🔐 CustomLoginView:
    - Replaces Django’s default login to use email instead of username.
    - Adds Google reCAPTCHA.
    - Supports 'keep me signed in' (long session).
    - Verifies user is marked as verified before allowing login.
    """

    template_name = 'users/login.html'            # Path to login template
    authentication_form = EmailLoginForm          # Custom email login form
    redirect_authenticated_user = True            # If already logged in, redirect to dashboard

    def get_context_data(self, **kwargs):
        """
        Injects extra context into the template:
        - reCAPTCHA site key
        - Whether to show reCAPTCHA (after 3 failed attempts)
        - Whether to show Google login button
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY
        context["show_recaptcha"] = self.request.session.get("login_attempts", 0) >= 3

        config = AuthConfig.objects.first()
        context["enable_google_login"] = config.enable_google_login if config else False
        return context

    def get_form_kwargs(self):
        """
        Passes request object to the form.
        Required for forms that need access to session (reCAPTCHA).
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """
        Called when login form is valid:
        - Verifies if user is_verified.
        - Handles 'keep me signed in' checkbox.
        - Logs in user using EmailBackend.
        """
        user = form.get_user()

        if user is None:
            messages.error(self.request, sysmsg.MESSAGES["LOGIN_FAILED"])
            return self.form_invalid(form)

        if not user.is_verified:
            messages.error(self.request, sysmsg.MESSAGES["ACCOUNT_NOT_ACTIVATED"])
            return self.form_invalid(form)

        login(self.request, user, backend='apps.users.authentication.EmailBackend')
        self.request.session["login_attempts"] = 0

        remember = self.request.POST.get('remember')
        self.request.session.set_expiry(60 * 60 * 24 * 30 if remember else 0)

        messages.success(self.request, sysmsg.MESSAGES["LOGIN_SUCCESS"])
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """
        Called when login form is invalid:
        - Increments login_attempts in session.
        - Useful for enabling reCAPTCHA after 3 fails.
        """
        self.request.session["login_attempts"] = self.request.session.get("login_attempts", 0) + 1
        print(f"Login attempts: {self.request.session.get('login_attempts')}")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Redirect URL after successful login.
        """
        return reverse_lazy('users:dashboard')


def logout_view(request):
    """
    🚪 Logs out the user:
    - If triggered by inactivity, shows warning.
    - Else, shows normal logout message.
    - Redirects to login page.
    """
    logout(request)

    if request.GET.get("auto") == "1":
        messages.warning(request, sysmsg.MESSAGES["AUTO_LOGOUT_WARNING"])
    else:
        messages.success(request, sysmsg.MESSAGES["LOGOUT_SUCCESS"])

    return redirect('users:login')
