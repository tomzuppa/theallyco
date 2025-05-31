# -----------------------------------------
# 🚫 BLOCKED PAGE VIEW (AFTER LIMIT EXCEEDED)
# -----------------------------------------

# 📦 Django Core
from django.views.generic import TemplateView  # Base view for rendering static templates

class BlockedView(TemplateView):
    """
    🚫 BlockedView:
    - Displayed when user exceeds allowed resend or verification attempts.
    - Simply renders a blocked.html template informing the user.

    Triggered from:
    - VerifyAccountView → resend flow
    - Token verification → if attempt count ≥ 3

    Template used:
    - 'users/blocked.html'
    """
    template_name = 'users/blocked.html'
