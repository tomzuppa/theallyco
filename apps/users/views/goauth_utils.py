# /apps/users/views/oauth_utils.py

# External OAuth library for Google
from google_auth_oauthlib.flow import Flow
# Django core settings
from django.conf import settings

def get_google_flow(state=None):
    """
    A helper function to build and configure the Google OAuth Flow object.
    This avoids repeating the configuration in multiple views.
    """
    # These are the permissions your application is requesting.
    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]

    # Create the flow instance from the configuration in settings.py
    flow = Flow.from_client_config(
        settings.GOOGLE_OAUTH2_CLIENT_CONFIG,
        scopes=scopes, # The requested scopes
        state=state  # The "state" parameter is used for CSRF protection.
    )

    # The URL to which Google will redirect the user after they grant consent.
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    return flow