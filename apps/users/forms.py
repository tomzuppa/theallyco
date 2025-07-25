# ✅ Django Forms – Cleaned, Commented, and Referenced (PEP8-compliant)

# ------------------------
# 📦 Django Form System
# ------------------------
from django import forms
from django.core.exceptions import ValidationError

# 🔐 Authentication tools
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# ⚙️ Settings and Environment
from django.conf import settings

# 🌐 HTTP requests for reCAPTCHA validation
import requests

# 💬 System messages
from project_root import messages as sysmsg

# 🔐 Token validation tools
from django.core.signing import loads, BadSignature, SignatureExpired

# Password reset
from django.contrib.auth.forms import PasswordResetForm

# Load the correct user model defined in AUTH_USER_MODEL
User = get_user_model()

# ------------------------
# 🧾 RegisterForm
# ------------------------
class RegisterForm(forms.ModelForm):
    """
    Custom registration form that includes:
    - Password confirmation
    - reCAPTCHA validation
    - Extra user profile fields

    Used in:
    - views.RegisterView (views.py)
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Password'
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Confirm Password'
        })
    )

    first_name = forms.CharField(label="First Name", widget=forms.TextInput(attrs={'class': 'login-dark-input'}))
    last_name = forms.CharField(label="Last Name", widget=forms.TextInput(attrs={'class': 'login-dark-input'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'login-dark-input'}))
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'login-dark-input'}))
    terms = forms.BooleanField(
        required=True,
        label="I agree to the Terms and Conditions"
    )
    phone = forms.CharField(required=False, label="Phone", widget=forms.TextInput(attrs={'class': 'login-dark-input'}))
    country = forms.CharField(required=False, label="Country", widget=forms.TextInput(attrs={'class': 'login-dark-input'}))
    postal_code = forms.CharField(required=False, label="Postal Code", widget=forms.TextInput(attrs={'class': 'login-dark-input'}))
    language = forms.ChoiceField(
        required=False,
        label="Preferred Language",
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        widget=forms.Select(attrs={'class': 'login-dark-input'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password1(self):
        """Validate password strength requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """

        password = self.cleaned_data.get("password1")

        if len(password) < 8:
            raise ValidationError(sysmsg.MESSAGES["PASSWORD_TOO_SHORT"])
        if not any(char.isupper() for char in password):
            raise ValidationError(sysmsg.MESSAGES["PASSWORD_NO_UPPER"])
        if not any(char.islower() for char in password):
            raise ValidationError(sysmsg.MESSAGES["PASSWORD_NO_LOWER"])
        if not any(char.isdigit() for char in password):
            raise ValidationError(sysmsg.MESSAGES["PASSWORD_NO_DIGIT"])
        if not any(not c.isalnum() for c in password):
            raise ValidationError(sysmsg.MESSAGES["PASSWORD_NO_SPECIAL"])
        
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(sysmsg.MESSAGES["PASSWORD_MISMATCH"])
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Overridden clean method to:
        - Normalize email and username to lowercase.
        - Validate reCAPTCHA response (if request object is available).
        """
        cleaned_data = super().clean()

        # 🔠 Normalize email and username to lowercase
        if 'email' in cleaned_data:
            cleaned_data['email'] = cleaned_data['email'].lower()
        if 'username' in cleaned_data:
            cleaned_data['username'] = cleaned_data['username'].lower()

        # ✅ reCAPTCHA validation (only if request is present)
        if not self.request:
            return cleaned_data  # Exit if request is not passed

        recaptcha_response = self.request.POST.get("g-recaptcha-response")
        if not recaptcha_response:
            self.add_error(None, sysmsg.MESSAGES["CAPTCHA_REQUIRED"])
            return cleaned_data

        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        response = requests.post(verify_url, data={
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response,
        })
        result = response.json()

        if not result.get("success"):
            raise forms.ValidationError(sysmsg.MESSAGES["CAPTCHA_INVALID"])

        return cleaned_data  # ✅ Always return cleaned_data at the end


# ------------------------
# 🔐 EmailLoginForm
# ------------------------
class EmailLoginForm(AuthenticationForm):
    """
    Custom login form that uses email instead of username.

    Replaces the default AuthenticationForm to allow login via email.

    Used in:
    - views.auth.CustomLoginView
    """

    def clean(self):
        """
        Overrides the default clean() method to:
        - Lowercase the email
        - Authenticate using the custom EmailBackend (email instead of username)
        """
        email = self.cleaned_data.get("username").lower()
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")

        return self.cleaned_data



# ------------------------
# 🔐 VerifyAccountForm (Manual token input - 2FA style)
# ------------------------
class VerifyAccountForm(forms.Form):
    """
    Token validation form (used in verify_account.html).
    Validates signed token received by email.

    Used in:
    - VerifyAccountView (views.py)
    """

    # 📬 Token input field (text box)
    token = forms.CharField(
        label="Activation Token",
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Enter your activation code'
        })
    )

    def clean_token(self):
        """
        Validates the token:
        - Ensures the token is not expired
        - Ensures the token has a valid signature
        - Extracts the email from the token payload
        """
        token = self.cleaned_data.get("token")

        try:
            # 🔐 Try to decode the token (valid for 5 minutes = 300 seconds)
            data = loads(token, max_age=300)

            # ✅ Store the email embedded in the token for further use
            self.cleaned_data["email"] = data.get("email")

        except SignatureExpired:
            # ⚠️ Token is expired
            raise forms.ValidationError(sysmsg.MESSAGES["TOKEN_EXPIRED"])

        except (BadSignature, KeyError):
            # ❌ Token is invalid (either tampered or incorrect structure)
            raise forms.ValidationError(sysmsg.MESSAGES["INVALID_TOKEN"])

        return token



# -----------------------------------
# 📬 Custom Password Reset Form
# Injects SITE_DOMAIN into email context
# -----------------------------------

class CustomPasswordResetForm(PasswordResetForm):
    def get_user_email_context(self):
        """
        🔧 Build context with correct domain and protocol for email templates.
        - Removes protocol from SITE_DOMAIN since it's passed separately.
        """
        return {
            'domain': settings.SITE_DOMAIN.replace("https://", "").replace("http://", ""),
            'protocol': "https"  # ✅ dynamic if needed
        }

    def send_mail(self, subject_template_name, email_template_name,
              context, from_email, to_email, html_email_template_name=None):
        """
        📤 Override send_mail to include friendly sender name like:
        'Administracion <mail@mail.com'
        """
        # 🧠 Add domain + protocol context 
        context.update(self.get_user_email_context())

        # 🏢 ✅ Inject COMPANY_NAME here
        context["COMPANY_NAME"] = settings.COMPANY_NAME

        # 🏷️ Compose subject manually
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())  # ✅ Remove newlines

        # 📨 Render plain text body
        body = render_to_string(email_template_name, context)

        # 👤 Full name + email format
        friendly_from = f"{settings.DEFAULT_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>"

        # 📬 Prepare email
        email_message = EmailMultiAlternatives(subject, body, friendly_from, [to_email])

        # 🧪 Optional: HTML body
        if html_email_template_name:
            html_body = render_to_string(email_template_name, context)
            email_message.attach_alternative(html_body, "text/html")
        
        print("[DEBUG] Email context:")
        print(context)


        # 🚀 Send it!
        email_message.send()
