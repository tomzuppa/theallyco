# ------------------------
# 🔐 Django AbstractUser for authentication extension
# ------------------------
from django.contrib.auth.models import AbstractUser  # Inherits Django's core user logic (username, password, groups, permissions, etc.)

# ------------------------
# 🧱 Django model base (ORM)
# ------------------------
from django.db import models

# ------------------------
# 🧱 To have the time zone of the active session

from django.utils import timezone


# ------------------------
 # Settings of the project (here we determine the custom )
from django.conf import settings



# ------------------------
# 👤 CustomUser model (extends AbstractUser)
# ------------------------
class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    🔐 Used as the main user class via AUTH_USER_MODEL in settings.py.

    ✅ Adds support for:
    - Email-based login
    - Google login integration
    - Profile picture
    - Account verification (2FA-like)
    - Extra profile fields (phone, country, postal code, language)

    Referenced in:
    - Login and registration views (views.py)
    - Forms like RegisterForm and EmailLoginForm (forms.py)
    - Token validation (activate_account)
    """

    # Email used as login credential (must be unique)
    email = models.EmailField(unique=True)

    # Optional profile picture (avatar)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Whether user verified their email address (via token)
    is_verified = models.BooleanField(default=False)

    # Optional contact fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    # Preferred language (used in i18n features)
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        default='en'
    )
    # ✅ Whether the user accepted terms and conditions during registration
    terms_accepted = models.BooleanField(default=False)


    # User Type Choices
    USER_TYPE_CHOICES = [
         ('employee', 'Aliad@')
        ,('client' , 'Cliente')
        ,('admin'   , 'Administrador')
    ]

    # User Type Field
    user_type = models.CharField(
          max_length = 10
        , choices=USER_TYPE_CHOICES
        , default='client'
        , help_text="Tipo de usuario: empleada doméstica, cliente o admin"
    )

    # 🧼 Force lowercase email and username
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)    

    def __str__(self):
        """
        Returns the username for admin display and logging purposes.
        """
        return self.username


# ------------------------
# 👩‍🍳 EmployeeProfile - Extended profile for 'employee' user type
# ------------------------
class EmployeeProfile(models.Model):
    """
    Extended profile model for users with user_type = 'employee' (Aliad@s del hogar).

    🧭 Used to:
    - Store personal and professional details of domestic workers
    - Enable geolocation-based filtering and matching
    - Attach documents like ID or recommendations

    Referenced in:
    - Views showing public employee profiles
    - Auto-created via signals on user registration (see signals.py)
    """
    # 🔗 Relation to CustomUser (One-to-One)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )

    # 🎂 Personal information
    age = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    # 💼 Services and availability
    services_offered = models.TextField(
        blank=True,
        help_text="Comma-separated list of services offered (e.g. limpieza, cocina, niños)"
    )
    work_area = models.CharField(
        max_length=100,
        blank=True,
        help_text="Preferred work area or neighborhood"
    )

    # 📍 Geolocation (used for maps & search)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Used to locate the employee on a map"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # 📎 Documents (e.g. ID, references)
    documents = models.FileField(
        upload_to='documents/',
        null=True,
        blank=True,
        help_text="Optional documents for identity or references"
    )

    # ⭐ Reputation system
    rating = models.FloatField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        """
        Display alias for admin or logging.
        """
        return f"Aliad@: {self.user.username}"



# ------------------------
# 🧑‍💼 ClientProfile - Extended profile for 'client' user type
# ------------------------
class ClientProfile(models.Model):
    """
    Extended profile model for users with user_type = 'client' (Employers).

    🧾 Used to:
    - Store optional billing and payment-related information
    - Prepare for future subscription or service tracking
    - Separate client-specific logic from the core user model

    Referenced in:
    - Views for client dashboards
    - Auto-created via signals on user registration (see signals.py)
    """

    # 🔗 Relation to CustomUser (One-to-One)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile'
    )

    # 💳 Payment setup (future use with Stripe, PayPal, etc.)
    default_payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Reference ID for preferred payment method"
    )

    billing_address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional billing address (used for invoices)"
    )

    # 🧾 Subscription status
    subscription_active = models.BooleanField(default=False)

    def __str__(self):
        """
        Display alias for admin or logging.
        """
        return f"Cliente: {self.user.username}"



# ------------------------
# 🎛️ AuthConfig (admin-toggleable authentication settings)
# ------------------------
class AuthConfig(models.Model):
    """
    Centralized configuration model for toggling authentication options.

    💡 Used to:
    - Enable/disable the Google login button from the admin panel
    - Plan for future features like password reset toggle, 2FA enforcement, etc.

    Referenced in:
    - CustomLoginView → renders Google login button conditionally
    - Django admin → editable via UI
    """

    enable_google_login = models.BooleanField(
        default=False,
        help_text="Enable login with Google"
    )

    # Auto-updated timestamp for auditing
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Display label in Django admin panel.
        """
        return "Authentication Settings"


# ------------------------
#  🗃️ Logs every password reset attempt in the system.
# ------------------------
class PasswordResetLog(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(default=timezone.now)
    successful = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    # 🆕 Device fields
    device_type = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        status = "✅" if self.successful else "❌"
        return f"[{status}] {self.email} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
