# ✅ project_root/messages.py
# --------------------------------------------------
# Centralized system messages for platform-wide use
# Used in: views, forms, templates (via Django messages framework)
# --------------------------------------------------

MESSAGES = {

    # 🔐 Authentication Flow (Login, Logout, Register)
    "LOGIN_SUCCESS": "Welcome back! Auto-logout in 15 minutes of inactivity.",
    "LOGIN_FAILED": "Invalid credentials, please try again.",
    "LOGOUT_SUCCESS": "You have been logged out successfully.",
    "REGISTER_SUCCESS": "Please, check your email to activate your account.",
    "EMAIL_ALREADY_USED": "This email address is already registered.",
    "USERNAME_ALREADY_USED": "This username is already taken.",
    "TERMS_REQUIRED": "You must accept the Terms and Conditions.",

    # 👤 Profile Management (reserved for future use)
    "PROFILE_UPDATED": "Your profile information has been updated.",
    "PASSWORD_CHANGED": "Your password has been changed successfully.",
    "PASSWORD_RESET_SENT": "Password reset instructions have been sent to your email.",

    # 🛡️ Security Features (auto logout, future 2FA toggles)
    "TWO_FACTOR_ENABLED": "Two-Factor Authentication has been enabled.",
    "TWO_FACTOR_DISABLED": "Two-Factor Authentication has been disabled.",
    "AUTO_LOGOUT_WARNING": "You have been logged out due to inactivity.",

    # ⚠️ Generic System Messages
    "GENERIC_ERROR": "An unexpected error occurred. Please try again.",
    "ACCESS_DENIED": "You do not have permission to access this page.",

    # 🔐 CAPTCHA (Google reCAPTCHA integration)
    "CAPTCHA_REQUIRED": "Please complete the reCAPTCHA.",
    "CAPTCHA_INVALID": "reCAPTCHA validation failed. Please try again.",

    # 📝 Registration Validations
    "PASSWORD_MISMATCH": "Passwords do not match.",

    # 🌐 Google OAuth2 Login
    "INVALID_STATE": "Invalid state parameter from Google login.",
    "USERINFO_FAILED": "Failed to fetch user info from Google.",
    "NO_GOOGLE_EMAIL": "Email not provided by Google.",

    # ✉️ Email Activation Flow
    "TOKEN_EXPIRED": "Activation link has expired. Please register again.",
    "INVALID_TOKEN": "Invalid or tampered activation link.",
    "VERIFIED_MAIL": "E-mail already verified.",
    "ACTIVATION_SUCCESS": "Account successfully activated. You can now log in.",
    "ACTIVATION_SUBJECT": "Activate your account",
    "ACCOUNT_NOT_ACTIVATED": "Your account is not activated yet. Please check your email and click the activation link.",
    "SESSION_EMAIL_MISSING": "We couldn't find your email session. Please register again.",
    "USER_NOT_FOUND": "Account not found. Please register again.",
    "ACTIVATION_RESENT": "We've re-sent your activation email. Please check your inbox.",
    "ACTIVATION_INSTRUCTIONS": "Enter the activation code we sent to your email. You can also request a new one if needed.",
    "ACTIVATION_TOKEN_REQUIRED": "Please enter your activation code to continue.",
    "RESEND_LIMIT_EXCEEDED": "You've exceeded the maximum resend attempts. Please register again with a different email."
}
