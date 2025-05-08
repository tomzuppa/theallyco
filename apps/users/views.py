from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from datetime import datetime
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib import messages
from .forms import EmailLoginForm # ✅ authentication.py
from project_root import messages as sysmsg  # import messages (central messages platform)
from django.conf import settings  # ✅ Required to access .env variables like RECAPTCHA keys
import requests  # ✅ Required to validate reCAPTCHA with Google's API
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from decouple import config, Csv  # Load .env variables
import requests
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth import get_user_model
User = get_user_model()
from google_auth_oauthlib.flow import Flow
from django.http import HttpResponseBadRequest
from .models import AuthConfig


import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ✅ Only for local or CloudShell testing

# ------------------------------------------------------------------------------
# 🔑 Custom LoginView with reCAPTCHA and 'Keep me signed in' functionality
# ------------------------------------------------------------------------------
class CustomLoginView(LoginView):
    """
    🔐 Custom login view with conditional reCAPTCHA and 'Keep me signed in' support.
    The form (EmailLoginForm) handles reCAPTCHA validation based on failed attempts.
    """
    template_name = 'users/login.html'
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        """
        🎯 Add reCAPTCHA public key and condition flag to context (used by template).
        """
        
        context = super().get_context_data(**kwargs)

        # 🔐 reCAPTCHA settings
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY
        context["show_recaptcha"] = self.request.session.get("login_attempts", 0) >= 3

        # 🔘 Google login toggle (from DB config)
        config = AuthConfig.objects.first()
        context["enable_google_login"] = config.enable_google_login if config else False
        
        return context

    def get_form_kwargs(self):
        """
        🔄 Pass the request to the form so it can access session (used for reCAPTCHA logic).
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """
        ✅ Login succeeded: reset login attempts, set session duration, show success message.
        """
        self.request.session["login_attempts"] = 0

        # 💾 Handle "Keep me signed in" option
        remember = self.request.POST.get('remember')
        self.request.session.set_expiry(60 * 60 * 24 * 30 if remember else 0)

        messages.success(self.request, sysmsg.MESSAGES["LOGIN_SUCCESS"])
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        ❌ Login failed: increase login attempts and show failure message.
        CAPTCHA validation is handled inside the form itself.
        """
        self.request.session["login_attempts"] = self.request.session.get("login_attempts", 0) + 1

        print("Login attempts:", self.request.session.get("login_attempts", 0))  # 👈 For debugging
         
        # messages.error(self.request, sysmsg.MESSAGES["LOGIN_FAILED"])
        return super().form_invalid(form)

    def get_success_url(self):
        """
        📍 Redirect path after successful login.
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
        If the form is valid, save the new user.
        You can also handle additional profile data here in the future.
        """
        form.save()
        messages.success(self.request, sysmsg.MESSAGES["REGISTER_SUCCESS"])  # 👈 Message of registration sucess
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
        return HttpResponseBadRequest("Invalid state parameter")

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
        return HttpResponseBadRequest("Failed to fetch user info from Google")

    user_data = userinfo_response.json()
    email = user_data.get("email")
    first_name = user_data.get("given_name", "")
    last_name = user_data.get("family_name", "")

    if not email:
        return HttpResponseBadRequest("Email not provided by Google")

    # 👥 Step 5: Find or create the user in Django
    user, created = User.objects.get_or_create(email=email, defaults={
        "username": email,  # 🧠 If using custom user model, adjust this
        "first_name": first_name,
        "last_name": last_name
    })

    # ✅ Step 6: Log in the user
    login(request, user)

    # 🏁 Step 7: Redirect to dashboard or homepage
    return redirect('users:dashboard')
