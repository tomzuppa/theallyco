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

# ⚙️ Settings and Environment
from django.conf import settings

# 🌐 HTTP requests for reCAPTCHA validation
import requests

# 💬 System messages
from project_root import messages as sysmsg

# 🔐 Token validation tools
from django.core.signing import loads, BadSignature, SignatureExpired

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
