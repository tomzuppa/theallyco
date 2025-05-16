# 📄 Core rendering & redirection
from django.shortcuts import render, redirect

# 🔐 Auth system: login/logout/session/user
from django.contrib.auth.views import LoginView                     # Used in CustomLoginView
from django.contrib.auth.decorators import login_required          # Used in dashboard protection
from django.contrib.auth import logout, login                      # Used in logout_view and Google login
from django.contrib.auth import get_user_model                     # Dynamically load CustomUser

# 🔐 Google OAuth2 flow
from google_auth_oauthlib.flow import Flow                         # Handles authorization redirects and token exchange

# 🔁 URL routing
from django.urls import reverse, reverse_lazy                      # reverse = for building URLs, reverse_lazy = for class views

# 🧠 Form views and validation
from django.views.generic import FormView                          # Used by RegisterView (class-based)
from django.http import HttpResponseBadRequest                     # Used to handle bad OAuth callbacks

# 📩 Forms
from .forms import RegisterForm                                    # Custom registration form (ModelForm)
from .forms import EmailLoginForm                                  # Custom login form with reCAPTCHA

# 📢 Messaging system (flash messages)
from django.contrib import messages                                # Django messages framework
from project_root import messages as sysmsg                        # Centralized system messages

# 📅 Utils
from datetime import datetime                                      # Used to show current date in dashboard

# 📬 Email system
from django.core.mail import send_mail                             # To send activation email
from django.template.loader import render_to_string                # To render email body from template

# ⚙️ Environment and settings
from django.conf import settings                                   # For accessing .env and Django settings
from decouple import config, Csv                                   # Preferred .env loader
from dotenv import load_dotenv                                     # Legacy .env loader (not used if decouple is used)

# 🌍 External API requests (Google reCAPTCHA / userinfo)
import requests                                                    # Used for reCAPTCHA and Google userinfo fetch

# 🔐 Token signing for activation
from django.core.signing import dumps, loads, BadSignature, SignatureExpired  # Token handling for secure email activation

# 🎛️ Models
from .models import AuthConfig                                     # Google login toggle model

# 🔧 Local testing config
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'                    # Allow OAuth over HTTP in dev

#Format to allows ASCI in the e mail sender name
from email.utils import formataddr
from email.header import Header
from django.core.mail import EmailMessage


User = get_user_model()
# ------------------------------------------------------------------------------
# 🔑 Custom LoginView with reCAPTCHA and 'Keep me signed in' functionality
# ------------------------------------------------------------------------------
class CustomLoginView(LoginView):
    """
    🔐 Custom login view that uses EmailLoginForm.
    ✅ Enforces reCAPTCHA after 3 failed attempts.
    ✅ Handles 'Keep me signed in'.
    ✅ Forces EmailBackend explicitly to avoid Django backend collisions.
    """
    template_name = 'users/login.html'
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        """
        🔧 Adds reCAPTCHA keys and Google login toggle to template context.
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY
        context["show_recaptcha"] = self.request.session.get("login_attempts", 0) >= 3

        config = AuthConfig.objects.first()
        context["enable_google_login"] = config.enable_google_login if config else False

        return context

    def get_form_kwargs(self):
        """
        💡 Passes request object to the form for access to session and POST data.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """
        ✅ Executes when the form is valid:
        - Uses forced login with EmailBackend.
        - Skips super().form_valid to avoid backend collisions.
        - Resets attempts, handles 'Keep me signed in'.
        """
        user = form.get_user()

        if user is None:
            messages.error(self.request, sysmsg.MESSAGES["LOGIN_FAILED"])
            return self.form_invalid(form)

        if not user.is_verified:
            messages.error(self.request, sysmsg.MESSAGES["ACCOUNT_NOT_ACTIVATED"])
            return self.form_invalid(form)

        # 🔐 Explicitly force backend to EmailBackend to avoid ValueError
        login(self.request, user, backend='apps.users.authentication.EmailBackend')

        self.request.session["login_attempts"] = 0

        remember = self.request.POST.get('remember')
        self.request.session.set_expiry(60 * 60 * 24 * 30 if remember else 0)

        messages.success(self.request, sysmsg.MESSAGES["LOGIN_SUCCESS"])

        # ⛳ Manual redirection (skip super().form_valid)
        return redirect(self.get_success_url())


    def form_invalid(self, form):
        """
        ❌ Login failed → increment attempts counter and show error.
        """
        self.request.session["login_attempts"] = self.request.session.get("login_attempts", 0) + 1
        print(f"Login attempts: {self.request.session.get('login_attempts')}")  # For debugging
        return super().form_invalid(form)

    def get_success_url(self):
        """
        🚀 Defines the landing page after successful login.
        """
        return reverse_lazy('users:dashboard')

# ----------------------------
# views.py in users app
# ----------------------------
# 🔐 Logs out the user and redirects to login page
def logout_view(request):
    # 🚪 Terminates the current session and logs out the user
    logout(request)

    # 🧠 Check if the logout was triggered by inactivity
    # 'auto=1' comes from the frontend (auto_logout.js)
    if request.GET.get("auto") == "1":
        # 📩 Show a specific message indicating auto-logout due to inactivity
        messages.warning(request, sysmsg.MESSAGES["AUTO_LOGOUT_WARNING"])
    else:
        # ✅ Normal logout initiated by the user
        messages.success(request, sysmsg.MESSAGES["LOGOUT_SUCCESS"])

    # 🔁 Redirect to login page after logout
    return redirect('users:login')



# ✅ Displays the base dashboard (placeholder version)
# 🛡️ Requires the user to be authenticated
@login_required
def dashboard_base(request):
    # 📅 Create context with current date formatted as: "Apr 18, 2025"
    current_date = datetime.now().strftime("%b %d, %Y")

    # 🧑‍💼 Get the username of the currently logged-in user
    user_name = request.user.username

    # 📦 Bundle the context data into a dictionary to pass to the template
    context = {
        'current_date': current_date,
        'username': user_name
    }

    # 🎨 Render the dashboard template and inject the context variables
    return render(request, 'dashboardb/dashboardb.html', context)



# 🧭 Class-based view for user registration
class RegisterView(FormView):
    template_name = "users/register.html"           # 📄 Template path
    form_class = RegisterForm                       # 📋 Form class to render and validate
    success_url = reverse_lazy('users:login')       # ✅ Redirect after successful registration

    def get_context_data(self, **kwargs):
        """
        Add the reCAPTCHA site key to the context so it can be used in the template.
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY  # 🔑 Loaded from .env
        return context

    def form_valid(self, form):
        """
        ✅ Handles valid user registration:
        - Saves the new user (is_verified = False)
        - Generates a signed activation token
        - Renders email template and sends activation email
        """

        # 💾 Save the user object from the validated form (creates CustomUser instance)
        user = form.save()

        # 🔐 Generate a signed token with email and user ID (valid for 24h by default)
        token = dumps({
            "email": form.cleaned_data["email"],
            "id": user.id
        })

        # 🔗 Reverse the URL pattern name to get the activation path
        activation_path = reverse('users:activate_account')  # Must match urls.py

        # 🌍 Build full activation URL using request context (absolute URI -- from settings/base.py --csrf trusted origins)
        activation_url = f"{settings.SITE_DOMAIN}{activation_path}?token={token}"

        # 📨 Load email body from external plain text template (cleaner than hardcoding)
        message = render_to_string('emails/activation_email.txt', {
            "user": user,
            "activation_url": activation_url
        })

        # ✉️ Build the FROM header (visible name + email) without affecting SMTP auth
        from_email_header = formataddr((
            str(Header(settings.DEFAULT_FROM_NAME, 'utf-8')),
            settings.DEFAULT_FROM_EMAIL
        ))

        # 📬 Build and send email using EmailMessage (ensures no auth error with SMTP)
        email = EmailMessage(
            subject=sysmsg.MESSAGES["ACTIVATION_SUBJECT"],
            body=message,
            #from_email_header,  # ✔️ Will show nicely in the inbox
            from_email= from_email_header, #settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.send(fail_silently=False)

        # ✅ Show success message via Django messages framework
        messages.success(self.request, sysmsg.MESSAGES["REGISTER_SUCCESS"])

        # 🔁 Proceed with normal redirection flow (to login page)
        return super().form_valid(form)


    def form_invalid(self, form):
        """
        If the form is invalid, show error messages.
        """
        #messages.error(self.request, sysmsg.MESSAGES["GENERIC_ERROR"])  # 👈 Message of error
        return super().form_invalid(form)
    
    # Google captcha
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # ✅ Here the info is sent
        return kwargs        

"""
Terms and Conditions for Registration Page (disabled for now)
"""
def terms(request):
    return render(request, 'legal/terms.html')




# ----------------------------
# Google login
# ----------------------------

def google_login(request):
    """
    🌐 View: google_login
    This view starts the Google OAuth2 login flow.
    It creates a secure authorization URL and redirects the user to Google's login page.

    🔗 Related Components:
        - Template: login.html (button that links to {% url 'google_login' %})
        - View: oauth2callback (will handle Google’s redirect back)
        - Security: Session-based CSRF protection via 'google_oauth_state'
        - .env file: where GOOGLE_CLIENT_ID, etc. are stored
    """

    # 🔐 Step 1: Configure the Google OAuth2 flow
    # Using manual client config to avoid relying on external credentials.json
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": config("GOOGLE_OAUTH_CLIENT_ID"),  # ↔️ Matches OAuth credentials from Google Cloud
                "client_secret": config("GOOGLE_OAUTH_CLIENT_SECRET"),  # 🛡️ Secure and private
                "redirect_uris": config("GOOGLE_REDIRECT_URI"),  # 🔁 Must match authorized redirect URI in Google Cloud
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",  # 📥 Google login endpoint
                "token_uri": "https://oauth2.googleapis.com/token"  # 📤 Where we'll exchange code for token
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]  # 📡 Required scopes to retrieve user email, name, and identity
    )

    # 📍 Set the redirect URI again, required by the flow object
    # 🔗 Used in oauth2callback to receive the token
    flow.redirect_uri = config("GOOGLE_REDIRECT_URI")

    # 🧬 Step 2: Generate the Google authorization URL and state token
    # state → used to protect the session against CSRF attacks
    authorization_url, state = flow.authorization_url(
        access_type='offline',                 # 💤 Allows future refresh token usage (optional)
        include_granted_scopes='true',        # ♻️ Retains existing permissions if re-authenticating
        prompt='consent'                      # 📋 Forces the consent screen every time
    )

    # 🛡️ Step 3: Store the state in session for security verification later
    # This will be validated in oauth2callback() to ensure integrity
    request.session['google_oauth_state'] = state

    # 🚀 Step 4: Redirect the user to Google's OAuth consent page
    return redirect(authorization_url)


def oauth2callback(request):
    """
    🔁 View: oauth2callback
    This view handles the redirect from Google after the user completes login.
    It verifies the security token (state), exchanges the code for tokens,
    fetches user data, and logs in or creates the user.

    🔗 Related to:
        - Session: 'google_oauth_state' (set in google_login view)
        - Google OAuth2 docs: exchanging code for token
        - Django's built-in login() and User model
    """

    # ⚠️ Step 1: Verify that state matches the session (CSRF protection)
    state_in_session = request.session.get('google_oauth_state')
    state_returned = request.GET.get('state')

    if not state_in_session or state_in_session != state_returned:
        return HttpResponseBadRequest(sysmsg.MESSAGES["INVALID_STATE"])

    # 🔐 Step 2: Reconstruct the Flow object
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

    # 🛠 Step 3: Exchange authorization code for access token
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    access_token = credentials.token

    # 🌐 Step 4: Use the token to get user info from Google
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

    # 👥 Step 5: Find or create the user in Django
    user, created = User.objects.get_or_create(email=email, defaults={
        "username": email,
        "first_name": first_name,
        "last_name": last_name
    })

    # ✅ Step 6: Force login and tell Django exactly which backend to use
    login(request, user, backend='apps.users.authentication.EmailBackend')

    # 🏁 Step 7: Redirect to dashboard or homepage
    return redirect('users:dashboard')

#----------------------------------------------------------------------
#TOKEN (ACCOUNT ACTIVATION)
#----------------------------------------------------------------------

def activate_account(request):
    """
    🌐 Handles user account activation via secure token.
    
    Triggered when user clicks the email confirmation link.
    The token is signed with SECRET_KEY and expires after 24 hours.

    🔗 Related:
    - Token generated with dumps() after registration
    - Linked to: /users/activate/?token=<signed_token>
    - Uses centralized MESSAGES system for feedback
    """

    token = request.GET.get("token")

    if not token:
        return HttpResponseBadRequest(sysmsg.MESSAGES["GENERIC_ERROR"])
        # Impacts: /users/activate/ with no token in URL

    try:
        # ✅ Extract signed data from token (email, id) and validate expiration
        data = loads(token, max_age=86400)  # 24 hours in seconds
        email = data["email"]

    except SignatureExpired:
        # ⛔ Token expired
        return HttpResponseBadRequest(sysmsg.MESSAGES["TOKEN_EXPIRED"])

    except (BadSignature, KeyError):
        # ⛔ Token modified or structure invalid
        return HttpResponseBadRequest(sysmsg.MESSAGES["INVALID_TOKEN"])

    try:
        # 👤 Fetch the user from DB using email
        user = User.objects.get(email=email)

    except User.DoesNotExist:
        # ⛔ If token is valid but email not found (edge case)
        return HttpResponseBadRequest(sysmsg.MESSAGES["NO_GOOGLE_EMAIL"])

    if user.is_verified:
        # ℹ️ User already activated – avoid redundant activation
        messages.info(request,  sysmsg.MESSAGES["VERIFIED_MAIL"])
        return redirect('users:login')

    # ✅ Activate the user account
    user.is_verified = True
    user.save()

    # 🎉 Show success message and redirect to login
    messages.success(request,  sysmsg.MESSAGES["ACTIVATION_SUCCESS"])
    return redirect('users:login')