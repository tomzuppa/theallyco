# -----------------------------------------
# 🌐 GOOGLE OAUTH2 LOGIN FLOW
# -----------------------------------------

# 📦 Django Core
from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.conf import settings

# 🌍 External Libraries & Project-specific imports
import requests
from project_root import messages as sysmsg
from .goauth_utils import get_google_flow # Import the new helper

# 🔐 Get the active user model from Django's auth system.
User = get_user_model()


def google_login(request):
    """
    🌐 Step 1: Initiates the Google OAuth2 login flow.
    """
    # Get the configured Google Flow object using our helper.
    flow = get_google_flow()

    # Generate the unique authorization URL for the user to visit.
    # The state is a random string used to prevent Cross-Site Request Forgery (CSRF).
    authorization_url, state = flow.authorization_url(
        access_type='offline',      # Indicates your app can refresh the token.
        prompt='consent',           # Always prompts the user for consent.
        include_granted_scopes='false' # Ensures all scopes are requested again.
    )

    # Store the CSRF state token in the user's session to verify it later.
    request.session['google_oauth_state'] = state
    
    # Redirect the user to the Google consent screen.
    return redirect(authorization_url)


def oauth2callback(request):
    """
    🔁 Step 2: Handles the callback from Google after user consent.
    """
    # Retrieve the original state token from the session.
    state_in_session = request.session.pop('google_oauth_state', None)
    # Get the state token returned by Google in the URL query parameters.
    state_returned = request.GET.get('state')

    # 🛡️ Verify the state token to protect against CSRF attacks.
    if not state_in_session or state_in_session != state_returned:
        messages.error(request, sysmsg.MESSAGES["INVALID_STATE"])
        return redirect('users:login') # Redirect to a safe page on failure.

    # Get the Flow object again, this time providing the state for validation.
    flow = get_google_flow(state=state_returned)

    try:
        # Exchange the authorization code (from the URL) for an access token.
        # This makes a secure, server-to-server request to Google.
        flow.fetch_token(authorization_response=request.build_absolute_uri())

        # Get the credentials object, which contains the access token.
        credentials = flow.credentials
        
        # 📞 Make a request to Google's userinfo endpoint to get profile data.
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={'access_token': credentials.token},
            timeout=5 # Set a timeout to prevent the request from hanging indefinitely.
        )
        # Raise an HTTPError if the HTTP request returned an unsuccessful status code.
        userinfo_response.raise_for_status()

    # 🥅 Catch potential network errors (e.g., timeout, connection error).
    except requests.exceptions.RequestException:
        messages.error(request, sysmsg.MESSAGES["USERINFO_FAILED"])
        return redirect('users:login')

    # Parse the JSON response from Google into a Python dictionary.
    user_data = userinfo_response.json()
    # Safely get the user's email from the data.
    email = user_data.get("email")

    # If Google did not return an email, the login cannot proceed.
    if not email:
        messages.error(request, sysmsg.MESSAGES["NO_GOOGLE_EMAIL"])
        return redirect('users:login')

    # --- Your Core Business Logic (Unchanged) ---
    try:
        # Find the user in your database corresponding to the Google email.
        user = User.objects.get(email=email)

        # Check if the user's account in your system has been verified.
        if not getattr(user, "is_verified", False):
            messages.warning(request, sysmsg.MESSAGES["ACCOUNT_NOT_VERIFIED"])
            return redirect('users:register')

    # If the user does not exist in your database...
    except User.DoesNotExist:
        messages.warning(request, sysmsg.MESSAGES["ACCOUNT_NOT_REGISTERED"])
        return redirect('users:register')

    # ✅ If the user exists and is verified, log them in.
    # Django will use the correct backend from your settings.py.
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    
    # Redirect the authenticated user to their dashboard.
    return redirect('users:dashboard')