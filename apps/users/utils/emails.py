# apps/users/utils/emails.py

# 📤 Email rendering and sending utilities
from django.template.loader import render_to_string           # Renders HTML/TXT templates with context
from django.utils.html import strip_tags                      # Strips HTML to create plain text fallback
from django.core.mail import EmailMultiAlternatives           # Allows sending both HTML + TXT in one email

# 🔧 Configuration and headers
from django.conf import settings                              # Access to settings like SITE_DOMAIN, etc.
from email.utils import formataddr                            # Formats display name + email
from email.header import Header                               # Ensures proper encoding of headers

# 💬 Centralized system messages
from project_root import messages as sysmsg

# 🔐 Token generator
from django.urls import reverse                               # Builds the relative URL for activation
from django.core.signing import dumps                         # Generates signed token with expiration control


def send_activation_email(user, request):
    """
    ✉️ Sends an activation email to the user using both HTML and plain text templates.

    Includes:
    - A secure 2FA-style token valid for 5 minutes
    - Optional link to the verify_account view
    - Support for centralized styling and company name injection

    Used in:
    - RegisterView
    - Email re-send logic (verify_account)
    """

    # 🧪 Generate a signed token with email + user ID
    token = dumps({
        "email": user.email,
        "id": user.id
    })

    # 🌐 Build a URL to redirect user to the token input page (used in the template)
    activation_path = reverse('users:verify_account')  # e.g., /users/verify-account/
    activation_url = f"{settings.SITE_DOMAIN}{activation_path}"

    # 🧠 Context passed to both HTML and plain-text templates
    context = {
        "user": user,
        "token": token,
        "activation_url": activation_url,
        "COMPANY_NAME": getattr(settings, 'COMPANY_NAME', 'Your Company'),
    }

    # 🖋 Render both HTML and plain-text bodies
    html_message = render_to_string('emails/activation_email.html', context)
    plain_message = render_to_string('emails/activation_email.txt', context)

    # 🧾 Format the From: field using display name and actual email
    from_email_header = formataddr((
        str(Header(settings.DEFAULT_FROM_NAME, 'utf-8')),
        settings.DEFAULT_FROM_EMAIL
    ))

    # 📬 Construct the email with subject and dual format (HTML + plain text)
    email = EmailMultiAlternatives(
        subject=sysmsg.MESSAGES["ACTIVATION_SUBJECT"],
        body=strip_tags(html_message),  # Plain text fallback for non-HTML clients
        from_email=from_email_header,
        to=[user.email],
    )
    email.attach_alternative(html_message, "text/html")  # Attach HTML version
    email.send(fail_silently=False)  # 💣 Fail visibly in dev for debugging
