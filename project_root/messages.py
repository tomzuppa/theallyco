# project_root/messages.py
# --------------------------------------------------
# Centralized system messages for platform-wide use
# Used in: views, forms, templates (via Django messages framework)
# --------------------------------------------------

MESSAGES = {

    # 🔐 AUTHENTICATION FLOW
    "LOGIN_SUCCESS": "Welcome back! You'll be automatically logged out after 15 minutes of inactivity.",
    "LOGIN_FAILED": "Invalid credentials. Please try again.",
    "LOGOUT_SUCCESS": "You have been logged out successfully.",
    "REGISTER_SUCCESS": "Please check your email to activate your account.",
    "EMAIL_ALREADY_USED": "This email address is already registered.",
    "USERNAME_ALREADY_USED": "This username is already taken.",
    "TERMS_REQUIRED": "You must accept the Terms and Conditions.",

    # 📝 REGISTRATION & VALIDATIONS
    "PASSWORD_MISMATCH": "Passwords do not match.",
    "PASSWORD_TOO_SHORT": "Password must be at least 8 characters long.",
    "PASSWORD_NO_UPPER": "Password must include at least one uppercase letter.",
    "PASSWORD_NO_LOWER": "Password must include at least one lowercase letter.",
    "PASSWORD_NO_DIGIT": "Password must include at least one number.",
    "PASSWORD_NO_SPECIAL": "Password must include at least one special character.",

    # ✉️ EMAIL ACTIVATION FLOW
    "ACTIVATION_INSTRUCTIONS": "A verification code has been sent to {email}. Please check it to complete your registration.",
    "ACTIVATION_TOKEN_REQUIRED": "Please enter your activation code to continue.",
    "ACTIVATION_SUCCESS": "Account successfully activated. You can now log in.",
    "ACTIVATION_RESENT": "We've re-sent your activation email. Please check your inbox.",
    "ACTIVATION_SUBJECT": "Activate your account",
    "ACCOUNT_NOT_ACTIVATED": "Your account is not activated yet. Please check your email and click the activation link.",
    "ACCOUNT_NOT_REGISTERED": "This account is not registered. Please sign up first.",
    "ACCOUNT_NOT_VERIFIED": "Your account is not verified. Please verify your email first.",
    "VERIFIED_MAIL": "E-mail already verified.",
    "SESSION_EMAIL_MISSING": "We couldn't find your email session. Please register again.",
    "USER_NOT_FOUND": "Account not found. Please register again.",
    "PREVIOUS_REGISTRATION_INCOMPLETE": "Your previous registration was not completed. Please start over.",
    "TOKEN_EXPIRED_PLEASE_RESTART": "Your verification code has expired. Please restart the registration process to receive a new one.",
    "TOKEN_EXPIRED_OR_INVALID_RESTART": "Your verification session has expired or is invalid. Please restart the registration.",
    "INVALID_TOKEN_ATTEMPTS": "Invalid verification code. You have {attempts_left} attempt(s) left.",
    "MAX_ATTEMPTS_EXCEEDED_BLOCKED": "You have exceeded the maximum number of attempts. Your session has been blocked. Please contact support or try again later.",
    "RESEND_LIMIT_EXCEEDED": "You've exceeded the maximum resend attempts. Please register again using a different email.",
    "ERROR_RESENDING_TOKEN": "An error occurred while trying to resend the code. Please try again.",
    "ERROR_SENDING_EMAIL": "Error sending verification email. Please try again.",

    # 🌐 GOOGLE OAUTH2 LOGIN
    "INVALID_STATE": "Invalid state parameter from Google login.",
    "USERINFO_FAILED": "Failed to fetch user info from Google.",
    "NO_GOOGLE_EMAIL": "Email was not provided by Google.",

    # 🛡️ SECURITY FEATURES
    "TWO_FACTOR_ENABLED": "Two-Factor Authentication has been enabled.",
    "TWO_FACTOR_DISABLED": "Two-Factor Authentication has been disabled.",
    "AUTO_LOGOUT_WARNING": "You have been logged out due to inactivity.",

    # 🧑‍💼 PROFILE MANAGEMENT (Future Use)
    "PROFILE_UPDATED": "Your profile information has been updated.",
    "PASSWORD_CHANGED": "Your password has been changed successfully.",
    "PASSWORD_RESET_SENT": "Password reset instructions have been sent to your email.",

    # 🤖 CAPTCHA (Google reCAPTCHA Integration)
    "CAPTCHA_REQUIRED": "Please complete the reCAPTCHA.",
    "CAPTCHA_INVALID": "reCAPTCHA validation failed. Please try again.",

    # ⚠️ GENERIC SYSTEM MESSAGES
    "GENERIC_ERROR": "An unexpected error occurred. Please try again.",
    "ACCESS_DENIED": "You do not have permission to access this page.",
}
