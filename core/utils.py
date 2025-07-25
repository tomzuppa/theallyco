# ✅ core/utils.py
# --------------------------------------------------
# Utility to fetch the latest branding info for signup page
# Used in: RegisterTokenView (users/views/register.py)
# --------------------------------------------------

from .models import SignupBranding
import requests
from django.conf import settings
from django.contrib import messages
from project_root import messages as sysmsg
from user_agents import parse


def get_signup_branding():
    return SignupBranding.objects.last()


# 📦 Utility Functions for Request User Metadata
# -----------------------------------------
# 🔍 Used in: views that need user context (IP, User-Agent, etc.)

def get_client_ip(request):
    """
    🔎 Get the client's IP address from the HTTP headers.
    
    - If using a proxy (like Cloud Run or Nginx), 'HTTP_X_FORWARDED_FOR' is more reliable.
    - Otherwise, fallback to REMOTE_ADDR.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request):
    """
    📱 Get the client's User-Agent string (browser, OS, device info).
    
    - Useful for logging, security checks, analytics, etc.
    """
    return request.META.get('HTTP_USER_AGENT', '')[:512]  # Optional truncation for database storage



#---------------------------------------------------
# 🔐 Validates Google's reCAPTCHA token server-side.
#---------------------------------------------------
def validate_recaptcha(request) -> bool:
    """
    Used in: login, register, password reset (or any public form).

    Returns:
        True if valid; False otherwise and sets system messages.
    """
    recaptcha_token = request.POST.get('g-recaptcha-response')

    if not recaptcha_token:
        messages.error(request, sysmsg.MESSAGES["CAPTCHA_REQUIRED"])
        return False

    data = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': recaptcha_token,
        'remoteip': request.META.get('REMOTE_ADDR'),
    }

    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = response.json()

        if result.get('success'):
            return True
        else:
            messages.error(request, sysmsg.MESSAGES["CAPTCHA_INVALID"])
            return False

    except requests.exceptions.RequestException:
        messages.error(request, sysmsg.MESSAGES["GENERIC_ERROR"])
        return False




#---------------------------------------------------
# 📱 Detect device type, browser, and OS from User-Agent string.
#---------------------------------------------------
def get_device_info(user_agent_str):
    """
    Detect device type, browser, and OS from User-Agent string.
    """
    ua = parse(user_agent_str)
    return {
        "device_type": "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC",
        "browser": ua.browser.family,
        "os": ua.os.family,
    }
