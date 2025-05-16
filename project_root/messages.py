# project_root/messages.py

"""
System messages for user feedback throughout the platform.
Centralized for easy maintenance and translation.
"""

MESSAGES = {

    # 🔐 Authentication Flow (Login, Logout, Register)
    "LOGIN_SUCCESS": "Welcome back! Auto-logout in 15 minutes of inactivity.",
    # Used in: CustomLoginView (form_valid)
    # Displayed on: Login success (dashboard redirection)

    "LOGIN_FAILED": "Invalid credentials, please try again.",
    # Used in: (optional) CustomLoginView (form_invalid)
    # Displayed on: Incorrect email/password submission

    "LOGOUT_SUCCESS": "You have been logged out successfully.",
    # Used in: logout_view
    # Displayed after manual logout

    "REGISTER_SUCCESS": "Registration completed. You can now log in.",
    # Used in: RegisterView (form_valid)
    # Displayed on: Successful account creation

    "EMAIL_ALREADY_USED": "This email address is already registered.",
    # (Optional validation logic)
    # Displayed when email is already in use

    "USERNAME_ALREADY_USED": "This username is already taken.",
    # (Optional validation logic)
    # Displayed when username is duplicated

    "TERMS_REQUIRED": "You must accept the Terms and Conditions.",
    # Used in: Register form validation
    # Displayed when checkbox is unchecked

    # 👤 Profile Management (future use)
    "PROFILE_UPDATED": "Your profile information has been updated.",
    "PASSWORD_CHANGED": "Your password has been changed successfully.",
    "PASSWORD_RESET_SENT": "Password reset instructions have been sent to your email.",
    # To be used in: profile settings, password reset view

    # 🛡️ Security Features
    "TWO_FACTOR_ENABLED": "Two-Factor Authentication has been enabled.",
    "TWO_FACTOR_DISABLED": "Two-Factor Authentication has been disabled.",
    # Used in: future 2FA management view

    "AUTO_LOGOUT_WARNING": "You have been logged out due to inactivity.",
    # Used in: logout_view
    # Triggered by: auto_logout.js

    # ⚠️ System & Access
    "GENERIC_ERROR": "An unexpected error occurred. Please try again.",
    "ACCESS_DENIED": "You do not have permission to access this page.",
    # Used for: generic error handling or unauthorized views

    # 🔐 CAPTCHA (Google reCAPTCHA)
    "CAPTCHA_REQUIRED": "Please complete the reCAPTCHA.",
    "CAPTCHA_INVALID": "reCAPTCHA validation failed. Please try again.",
    # Used in: EmailLoginForm and RegisterForm (clean)

    # 📝 Registration-specific validation
    "PASSWORD_MISMATCH": "Passwords do not match.",
    # Used in: RegisterForm (clean_password2)

    # 🌐 Google OAuth2 Login Flow
    "INVALID_STATE": "Invalid state parameter from Google login.",
    "USERINFO_FAILED": "Failed to fetch user info from Google.",
    "NO_GOOGLE_EMAIL": "Email not provided by Google.",

    # 🌐 E mail activation (token management)
    "TOKEN_EXPIRED": "Activation link has expired. Please register again.",
    "INVALID_TOKEN": "Invalid or tampered activation link.",
    "VERIFIED_MAIL": "E-mail already verified.",
    "ACTIVATION_SUCCESS": "Account successfully activated. You can now log in.",
    "ACTIVATION_SUBJECT": "Activate your account",
    "ACCOUNT_NOT_ACTIVATED":"Your account is not activated yet. Please check your email and click the activation link.",
    "REGISTER_SUCCESS":"Please, check your email to activate your account."

}
