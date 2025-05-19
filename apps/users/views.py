# ------------------------
# 🔧 Django Core Imports
# ------------------------
from django.shortcuts import render, redirect  # Core rendering and redirection for views
from django.http import HttpResponseBadRequest  # To return HTTP 400 bad request responses
from django.urls import reverse, reverse_lazy  # For generating URLs by name (lazy for class-based views)

# ------------------------
# 🔐 Authentication & User Management
# ------------------------
from django.contrib.auth.views import LoginView  # Django's built-in LoginView (to customize)
from django.contrib.auth.decorators import login_required  # Decorator to protect views for logged-in users
from django.contrib.auth import logout, login  # Login/logout user functions (session-based)
from django.contrib.auth import get_user_model  # Dynamically loads the User model from settings
from django.views.decorators.csrf import csrf_protect  # CSRF protection for forms
from django.utils.decorators import method_decorator  # To apply decorators on class-based views

# ------------------------
# 📬 Forms & Models
# ------------------------
from django.views.generic import FormView, TemplateView  # Base classes for form and template views
from .forms import RegisterForm, EmailLoginForm, VerifyAccountForm  # Custom forms used in the flow
from .models import AuthConfig  # Model used to toggle Google login availability

# ------------------------
# 📢 Messaging System
# ------------------------
from django.contrib import messages  # Django flash messages framework (user notifications)
from project_root import messages as sysmsg  # Centralized messages (customized for project)

# ------------------------
# 📬 Emails & Token Handling
# ------------------------
from django.core.signing import dumps, loads, BadSignature, SignatureExpired  # Token generation & validation (used in activation)
from .utils.emails import send_activation_email  # Custom utility to send activation emails (utils/emails.py)

# ------------------------
# 🕒 Utilities & Config
# ------------------------
from datetime import datetime  # Date/time utilities
from django.conf import settings  # Django settings access (used for site domain, keys, etc.)
from decouple import config  # .env file loader for secure environment variables

# ------------------------
# 🌍 External APIs & OAuth
# ------------------------
import requests  # Used for external APIs (Google reCAPTCHA, Google userinfo, etc.)
from google_auth_oauthlib.flow import Flow  # Manages Google OAuth2 login flow

# ------------------------
# ⚙️ Local Testing Config (DEV ONLY - HIGH RISK in production)
# ------------------------
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ❗ Allows OAuth over HTTP (should be active ONLY in DEV environments)

# ------------------------
# 🔐 User Model Instance (Loaded once globally)
# ------------------------
User = get_user_model()  # Loads the custom user model (from settings.AUTH_USER_MODEL)


# ------------------------
# 🔐 Custom LOGIN VIEW (EmailLoginForm + reCAPTCHA + 'Keep me signed in')
# ------------------------
class CustomLoginView(LoginView):
    """
    🔐 CustomLoginView:
    - Extends Django's LoginView to support email-based login using EmailLoginForm.
    - Enforces reCAPTCHA after 3 failed login attempts.
    - Implements 'Keep me signed in' logic by adjusting session expiry.
    - Forces explicit backend usage to avoid conflicts (important when custom backends are active).

    Related Forms:
    - EmailLoginForm (from forms.py)
    - AuthConfig (model used to toggle Google login button)
    """
    template_name = 'users/login.html'  # Template to render the login form
    authentication_form = EmailLoginForm  # Custom form using email instead of username
    redirect_authenticated_user = True  # Auto-redirect if already logged in

    def get_context_data(self, **kwargs):
        """
        Adds extra context to the login template:
        - reCAPTCHA site key (loaded from settings)
        - Show reCAPTCHA if login attempts >= 3 (stored in session)
        - Google login button visibility (from AuthConfig model)
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY
        context["show_recaptcha"] = self.request.session.get("login_attempts", 0) >= 3
        config = AuthConfig.objects.first()  # Gets Google login toggle config (only first row expected)
        context["enable_google_login"] = config.enable_google_login if config else False
        return context

    def get_form_kwargs(self):
        """
        Passes the request object to the form.
        Important for forms that need access to session (e.g., for reCAPTCHA).
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """
        Handles the case when the login form is valid:
        - Retrieves the validated user.
        - Verifies if the user is marked as verified (custom user field: is_verified).
        - Logs the user in using the custom EmailBackend.
        - Resets the login attempts counter.
        - Manages 'Keep me signed in' by setting session expiry.
        - Shows success message and redirects to dashboard.
        """
        user = form.get_user()  # Gets the user validated in the form

        if user is None:
            messages.error(self.request, sysmsg.MESSAGES["LOGIN_FAILED"])
            return self.form_invalid(form)

        if not user.is_verified:
            messages.error(self.request, sysmsg.MESSAGES["ACCOUNT_NOT_ACTIVATED"])
            return self.form_invalid(form)

        # Logs in using the custom backend (defined in authentication.py)
        login(self.request, user, backend='apps.users.authentication.EmailBackend')

        # Resets login attempts counter
        self.request.session["login_attempts"] = 0

        # Checks if 'remember' was selected (checkbox in form), and sets session expiry accordingly
        remember = self.request.POST.get('remember')
        self.request.session.set_expiry(60 * 60 * 24 * 30 if remember else 0)

        messages.success(self.request, sysmsg.MESSAGES["LOGIN_SUCCESS"])
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """
        Handles invalid form submission (wrong credentials):
        - Increments the login attempt counter in session.
        - Logs the attempt in console (for debugging).
        - Returns the form with errors.
        """
        self.request.session["login_attempts"] = self.request.session.get("login_attempts", 0) + 1
        print(f"Login attempts: {self.request.session.get('login_attempts')}")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Defines the redirection after successful login.
        """
        return reverse_lazy('users:dashboard')


# ------------------------
# 🔐 LOGOUT VIEW
# ------------------------
def logout_view(request):
    """
    Logs out the user.
    - Destroys the current session.
    - Checks if the logout was triggered by inactivity ('auto=1' in GET params).
    - Displays an appropriate flash message depending on the reason.
    - Redirects the user to the login page.
    """
    logout(request)  # Destroys the current session and logs out the user

    # Checks if the logout was triggered by auto_logout.js (adds 'auto=1' param)
    if request.GET.get("auto") == "1":
        messages.warning(request, sysmsg.MESSAGES["AUTO_LOGOUT_WARNING"])  # Shows auto-logout message
    else:
        messages.success(request, sysmsg.MESSAGES["LOGOUT_SUCCESS"])  # Shows normal logout message

    return redirect('users:login')  # Redirects always to login page after logout


# ------------------------
# 🛡️ DASHBOARD PROTECTED VIEW (DUMMY EXAMPLE)
# ------------------------
@login_required
def dashboard_base(request):
    """
    Displays a basic dashboard page.
    - Requires the user to be authenticated (protected with @login_required).
    - Shows current date and logged-in username.
    - Placeholder version, to be customized as needed.

    Template used:
    - 'dashboardb/dashboardb.html'
    """
    current_date = datetime.now().strftime("%b %d, %Y")  # Gets current date as string (e.g., "May 17, 2025")
    user_name = request.user.username  # Gets username from authenticated user

    # Bundles data into context dictionary
    context = {
        'current_date': current_date,
        'username': user_name
    }

    return render(request, 'dashboardb/dashboardb.html', context)  # Renders the dashboard page with context


# ------------------------
# 📝 REGISTRATION VIEW
# ------------------------
class RegisterView(FormView):
    """
    Handles the user registration flow.
    - Uses RegisterForm (custom form defined in forms.py).
    - After registration, sends activation email using send_activation_email (utils/emails.py).
    - Saves the email temporarily in session for resend functionality.
    - Redirects to verify_account view instead of login directly.

    Template used:
    - 'users/register.html'
    """
    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy('users:login')  # Not used directly (we override form_valid to redirect manually)

    def get_context_data(self, **kwargs):
        """
        Adds context data to the registration template.
        - Includes reCAPTCHA site key (from settings).
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY  # Loaded from your .env or settings
        return context

    def form_valid(self, form):
        """
        Called when the form is valid:
        - Saves the new user to the database (using form.save()).
        - Stores user's email in session for resend flow.
        - Sends activation email using utils/emails.py.
        - Shows success message.
        - Redirects to verify_account view.
        """
        user = form.save()  # Creates and saves the user object

        # Stores email in session to allow resend flow (handled in VerifyAccountView)
        self.request.session['pending_activation_email'] = user.email

        # Sends the activation email (handled by reusable function in utils/emails.py)
        send_activation_email(user, self.request)

        messages.success(self.request, sysmsg.MESSAGES["REGISTER_SUCCESS"])  # Shows success message
        return redirect('users:verify_account')  # Redirects to token verification screen

    def form_invalid(self, form):
        """
        If form is invalid:
        - Returns form with errors.
        """
        return super().form_invalid(form)

    def get_form_kwargs(self):
        """
        Ensures the request object is passed to the form.
        - Needed for Google reCAPTCHA validation inside the form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# ------------------------
# 📄 TERMS & CONDITIONS STATIC PAGE
# ------------------------
def terms(request):
    """
    Renders the terms and conditions static page.
    - Uses 'legal/terms.html'.
    - This is a placeholder and can be extended or linked to dynamic content.
    """
    return render(request, 'legal/terms.html')


# ------------------------
# 🔐 VERIFY ACCOUNT 2FA-STYLE FLOW (TOKEN & RESEND CENTRALIZED)
# ------------------------
@method_decorator(csrf_protect, name='dispatch')
class VerifyAccountView(TemplateView):
    """
    View: VerifyAccountView (2FA-style centralized page)
    - Handles the account verification using a token.
    - Allows resending the activation email (with resend limit protection).
    - If user exceeds resend attempts, redirects to blocked page.
    - All handled within the same view to simulate a 2FA flow.

    Template used:
    - 'users/verify_account.html'
    """

    template_name = "users/verify_account.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden dispatch method.
        - Checks BEFORE any action if the user exceeded allowed resend attempts.
        - If so, clears session and redirects to blocked page.
        - This makes the block unavoidable even if user tries to bypass frontend JS.
        """
        if request.session.get('resend_attempts', 0) >= 3:
            # Clean session and redirect to blocked page
            request.session.pop('pending_activation_email', None)
            request.session.pop('resend_attempts', None)
            messages.error(request, sysmsg.MESSAGES["RESEND_LIMIT_EXCEEDED"])
            return redirect('users:blocked')

        # If OK, proceeds as normal
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Adds form and attempt status to the template context.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = VerifyAccountForm()  # Provides the token form (from forms.py)
        context["resend_attempts"] = self.request.session.get('resend_attempts', 0)
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests.
        - If 'resend' is in POST data → calls handle_resend().
        - Else → calls handle_token_validation().
        """
        if 'resend' in request.POST:
            return self.handle_resend(request)
        return self.handle_token_validation(request)

    def handle_resend(self, request):
        """
        Handles the resend of activation email.
        - Checks session for pending email.
        - Validates resend limit again (double validation for safety).
        - Sends activation email using utils/emails.py.
        - Increments resend counter in session.
        """
        email = request.session.get('pending_activation_email')
        if not email:
            messages.error(request, sysmsg.MESSAGES["SESSION_EMAIL_MISSING"])
            return redirect('users:register')

        resend_attempts = request.session.get('resend_attempts', 0)

        if resend_attempts >= 3:
            # Extra redundancy even though dispatch protects it
            request.session.pop('pending_activation_email', None)
            request.session.pop('resend_attempts', None)
            messages.error(request, sysmsg.MESSAGES["RESEND_LIMIT_EXCEEDED"])
            return redirect('users:blocked')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, sysmsg.MESSAGES["USER_NOT_FOUND"])
            return redirect('users:register')

        send_activation_email(user, request)  # Calls utility function from utils/emails.py
        messages.success(request, sysmsg.MESSAGES["ACTIVATION_RESENT"])

        # Increments resend attempts counter
        request.session['resend_attempts'] = resend_attempts + 1

        return redirect('users:verify_account')

    def handle_token_validation(self, request):
        """
        Handles token validation flow.
        - Validates the token submitted by the user.
        - If valid → activates the account.
        - If already verified → redirects to login.
        - If invalid → reloads page showing errors.
        """
        form = VerifyAccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, sysmsg.MESSAGES["USER_NOT_FOUND"])
                return redirect('users:register')

            if user.is_verified:
                messages.info(request, sysmsg.MESSAGES["VERIFIED_MAIL"])
                return redirect('users:login')

            user.is_verified = True  # Marks user as verified (custom field in user model)
            user.save()
            messages.success(request, sysmsg.MESSAGES["ACTIVATION_SUCCESS"])
            return redirect('users:login')

        # If invalid token, returns form with errors
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)

# ------------------------
# 🌐 GOOGLE OAUTH2 LOGIN FLOW
# ------------------------
def google_login(request):
    """
    Starts the Google OAuth2 login flow.
    - Generates a secure authorization URL.
    - Redirects the user to Google's login page.

    Uses:
    - Flow from google_auth_oauthlib.
    - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI from .env (loaded via decouple).
    - Session key 'google_oauth_state' for CSRF protection.

    Related template:
    - 'users/login.html' (Google login button)
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": config("GOOGLE_OAUTH_CLIENT_ID"),
                "client_secret": config("GOOGLE_OAUTH_CLIENT_SECRET"),
                "redirect_uris": config("GOOGLE_REDIRECT_URI"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]
    )

    flow.redirect_uri = config("GOOGLE_REDIRECT_URI")

    # Generate authorization URL and state token for CSRF protection
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    # Store state in session to validate in callback
    request.session['google_oauth_state'] = state

    return redirect(authorization_url)


def oauth2callback(request):
    """
    Handles the callback from Google OAuth2.
    - Validates CSRF state token.
    - Exchanges code for access token.
    - Retrieves user info.
    - Logs in or creates the user.
    - Uses custom EmailBackend.

    On success → redirects to dashboard.
    """
    state_in_session = request.session.get('google_oauth_state')
    state_returned = request.GET.get('state')

    if not state_in_session or state_in_session != state_returned:
        return HttpResponseBadRequest(sysmsg.MESSAGES["INVALID_STATE"])

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": config("GOOGLE_OAUTH_CLIENT_ID"),
                "client_secret": config("GOOGLE_OAUTH_CLIENT_SECRET"),
                "redirect_uris": config("GOOGLE_REDIRECT_URI"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"],
        state=state_returned
    )

    flow.redirect_uri = config("GOOGLE_REDIRECT_URI")
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    access_token = credentials.token

    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={'access_token': access_token}
    )

    if not userinfo_response.ok:
        return HttpResponseBadRequest(sysmsg.MESSAGES["USERINFO_FAILED"])

    user_data = userinfo_response.json()
    email = user_data.get("email")
    first_name = user_data.get("given_name", "")
    last_name = user_data.get("family_name", "")

    if not email:
        return HttpResponseBadRequest(sysmsg.MESSAGES["NO_GOOGLE_EMAIL"])

    user, created = User.objects.get_or_create(email=email, defaults={
        "username": email,
        "first_name": first_name,
        "last_name": last_name
    })

    login(request, user, backend='apps.users.authentication.EmailBackend')

    return redirect('users:dashboard')


# ------------------------
# 🔐 ACCOUNT ACTIVATION FLOW VIA TOKEN (EMAIL LINK)
# ------------------------
def activate_account(request):
    """
    Handles user account activation via secure token (from email link).
    - Validates token (expires in 5 minutes).
    - Activates the user if valid and not yet verified.
    - Shows appropriate message.

    Token format:
    - Generated with dumps() in send_activation_email.
    - Includes email and id.

    URL format:
    - /users/activate/?token=<signed_token>
    """
    token = request.GET.get("token")
    if not token:
        return HttpResponseBadRequest(sysmsg.MESSAGES["GENERIC_ERROR"])

    try:
        data = loads(token, max_age=30)  # Token expires in 5 minutes (300 seconds)
        email = data["email"]
    except SignatureExpired:
        return HttpResponseBadRequest(sysmsg.MESSAGES["TOKEN_EXPIRED"])
    except (BadSignature, KeyError):
        return HttpResponseBadRequest(sysmsg.MESSAGES["INVALID_TOKEN"])

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return HttpResponseBadRequest(sysmsg.MESSAGES["NO_GOOGLE_EMAIL"])

    if user.is_verified:
        messages.info(request, sysmsg.MESSAGES["VERIFIED_MAIL"])
        return redirect('users:login')

    user.is_verified = True
    user.save()
    messages.success(request, sysmsg.MESSAGES["ACTIVATION_SUCCESS"])
    return redirect('users:login')


# ------------------------
# 🚨 BLOCKED PAGE (AFTER RESEND LIMIT EXCEEDED)
# ------------------------
class BlockedView(TemplateView):
    """
    Displays the blocked page after user exceeded allowed resend attempts.
    - Uses 'users/blocked.html'.
    """
    template_name = 'users/blocked.html'


# ------------------------
# 🚨 Legacy / Potentially Unused Code (Review before commenting out)
# ------------------------
"""
✅ These imports are currently present but NOT used anywhere in views.py:
- from django.core.mail import send_mail
- from django.core.mail import EmailMessage
- from email.utils import formataddr
- from email.header import Header

💡 Analysis:
- All email sending is handled via the reusable function 'send_activation_email' (utils/emails.py) using 'EmailMultiAlternatives'.
- These imports are redundant and safe to remove or comment.
- They have no impact on the system behavior currently.

💡 Proposal:
- Comment or delete safely.
- Risk: NONE.
- ✅ Recommendation: Leave commented and documented as backup.

⚙️ Keep them commented here for backup:
# from django.core.mail import send_mail
# from django.core.mail import EmailMessage
# from email.utils import formataddr
# from email.header import Header

❗ Additional critical observation:
- os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' is currently ALWAYS active.
- HIGH RISK if system ever runs in production without HTTPS.
- 💡 Proposal: Move inside 'if settings.DEBUG:' or restrict to local dev only.
"""
