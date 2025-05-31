# ------------------------------------------------------------------------------------------------
# 📧 apps/users/utils/emails.py – Email sending utilities for activation (2FA-style tokens)
# ------------------------------------------------------------------------------------------------

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from email.utils import formataddr
from email.header import Header
from django.conf import settings
from project_root import messages as sysmsg

from django.core.signing import dumps, loads  # Custom serializer


# ------------------------------------------------------------------------------------------------
# ✅ MAIN VERSION: Used for users who already exist in DB (has .email and .id attributes)
# ------------------------------------------------------------------------------------------------
def send_activation_email(user, request):
    """
    Sends an activation email with a secure token for a user that already exists in the database.
    
    - Uses `dumps()` to generate a signed token containing the user's email and ID.
    - Sends both HTML and plain-text versions of the email.
    - Includes the verification URL.
    """

    # 🔐 Generate signed token with user data (secure and time-based)
    token = dumps({
        "email": user.email,
        "id": user.id
    })

    # 🔗 Build the activation URL
    activation_path = reverse('users:verify_account')  # e.g. /users/verify-account/
    activation_url = f"{settings.SITE_DOMAIN}{activation_path}"

    # 📦 Context passed to the email templates
    context = {
        "user": user,
        "token": token,
        "activation_url": activation_url,
        "COMPANY_NAME": getattr(settings, 'COMPANY_NAME', 'Your Company'),
    }

    # 🖼 Render both HTML and plain-text email versions
    html_message = render_to_string('emails/activation_email.html', context)
    plain_message = render_to_string('emails/activation_email.txt', context)

    # 📨 Format sender name and address
    from_email_header = formataddr((
        str(Header(settings.DEFAULT_FROM_NAME, 'utf-8')),
        settings.DEFAULT_FROM_EMAIL
    ))

    # 📧 Create and send the email with both formats
    email = EmailMultiAlternatives(
        subject=sysmsg.MESSAGES["ACTIVATION_SUBJECT"],
        body=strip_tags(html_message),
        from_email=from_email_header,
        to=[user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)

# ------------------------------------------------------------------------------------------------
# 🆕 ALTERNATIVE VERSION: Used before the user is saved (only has email as string)
# ------------------------------------------------------------------------------------------------
def send_activation_email_from_token(email, request, token_part_b, expiry_minutes=settings.ACTIVATION_TOKEN_EXPIRY // 60):
    """
    Sends an activation email for a user that hasn't been saved in the database yet.
    
    - Uses the partial token (token_part_b) only.
    - Keeps the secure part server-side (token_part_a is stored in session).
    - Expected to be used in RegisterTokenView.
    """

    # 🔗 Build the activation URL to which the user should paste the code
    activation_path = reverse('users:register')  # e.g. /users/register/
    activation_url = f"{settings.SITE_DOMAIN}{activation_path}"

    # 📦 Context passed to the email templates
    context = {
        "user": {
            "first_name": "New User"  # Only shown if template uses it
        },
        "token_part_b": token_part_b,  # Only the visible part of the token is sent
        "activation_url": activation_url,
        "COMPANY_NAME": getattr(settings, 'COMPANY_NAME', 'Your Company'),
        "expiry_minutes": expiry_minutes,
    }

    # 🖼 Render both HTML and plain-text email versions
    html_message = render_to_string('emails/activation_email.html', context)
    plain_message = render_to_string('emails/activation_email.txt', context)

    # 📨 Format sender name and address
    from_email_header = formataddr((
        str(Header(settings.DEFAULT_FROM_NAME, 'utf-8')),
        settings.DEFAULT_FROM_EMAIL
    ))

    # 📧 Create and send the email with both formats
    email = EmailMultiAlternatives(
        subject=sysmsg.MESSAGES["ACTIVATION_SUBJECT"],
        body=strip_tags(plain_message),
        from_email=from_email_header,
        to=[email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
