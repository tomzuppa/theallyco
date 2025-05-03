# project_root/messages.py

"""
System messages for user feedback throughout the platform.
Centralized for easy maintenance and translation.
"""

MESSAGES = {
    # Authentication
    "LOGIN_SUCCESS": "Welcome back! Auto-logout in 15 minutes of inactivity.",
    "LOGIN_FAILED": "Invalid credentials, please try again.",
    "LOGOUT_SUCCESS": "You have been logged out successfully.",
    "REGISTER_SUCCESS": "Registration completed. You can now log in.",
    "EMAIL_ALREADY_USED": "This email address is already registered.",
    "USERNAME_ALREADY_USED": "This username is already taken.",
    "TERMS_REQUIRED": "You must accept the Terms and Conditions.",

    # Profile Management
    "PROFILE_UPDATED": "Your profile information has been updated.",
    "PASSWORD_CHANGED": "Your password has been changed successfully.",
    "PASSWORD_RESET_SENT": "Password reset instructions have been sent to your email.",

    # Security
    "TWO_FACTOR_ENABLED": "Two-Factor Authentication has been enabled.",
    "TWO_FACTOR_DISABLED": "Two-Factor Authentication has been disabled.",
    "AUTO_LOGOUT_WARNING": "You have been logged out due to inactivity.",

    # System
    "GENERIC_ERROR": "An unexpected error occurred. Please try again.",
    "ACCESS_DENIED": "You do not have permission to access this page.",
}
