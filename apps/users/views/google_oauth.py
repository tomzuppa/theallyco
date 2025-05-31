# -----------------------------------------
# 🌐 GOOGLE OAUTH2 LOGIN FLOW
# -----------------------------------------

# 📦 Django Core
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages
from project_root import messages as sysmsg



# 🌍 External OAuth and Config
import requests
from google_auth_oauthlib.flow import Flow
from decouple import config

# 🔐 Get the active user model
User = get_user_model()


def google_login(request):
    """
    🌐 Step 1: Initiates Google OAuth2 login
    - Builds authorization URL from client credentials.
    - Stores state token in session.
    - Redirects to Google's OAuth consent screen.
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

    # 🔐 Generate secure OAuth URL and CSRF state
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    request.session['google_oauth_state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    """
    🔁 Step 2: Handles Google's OAuth2 callback
    - Validates CSRF state.
    - Exchanges code for access token.
    - Retrieves user info from Google.
    - Logs in only if the user already exists and is verified.
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
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ],
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

    # 🔐 Only allow Google login if the user is already registered and verified
    try:
        user = User.objects.get(email=email)

        if not getattr(user, "is_verified", False):
            messages.warning(request, sysmsg.MESSAGES["ACCOUNT_NOT_VERIFIED"])
            return redirect('users:register')# Redirect to register or verification page
            
    except User.DoesNotExist:
        # 🛑 Do not allow login if user does not exist
        messages.warning(request, sysmsg.MESSAGES["ACCOUNT_NOT_REGISTERED"])
        return redirect('users:register')

    # ✅ Login user using custom backend
    login(request, user, backend='apps.users.authentication.EmailBackend')
    return redirect('users:dashboard')
