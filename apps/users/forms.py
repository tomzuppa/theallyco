# 📦 Django form system for handling user input and validation
from django import forms
from django.core.exceptions import ValidationError

# ✅ Ensures compatibility with AUTH_USER_MODEL defined in settings.py
from django.contrib.auth import get_user_model

# 🔐 Used as the base form for login functionality (username + password)
from django.contrib.auth.forms import AuthenticationForm

# ⚙️ Access environment variables like reCAPTCHA secret
from django.conf import settings

# 🌐 Used to validate reCAPTCHA tokens with Google's API
import requests

# 📩 Centralized system message platform (custom app messages)
from project_root import messages as sysmsg

from django.contrib.auth import authenticate  # ✅ Required for manual login validation

# 🎯 Get the correct user model (CustomUser)
User = get_user_model()

"""-------------------------------------------------------------------------------
-------------------------------------------------------------------------------"""

User = get_user_model()  # ✅ This ensures you're using CustomUser correctly

# 🧾 Custom registration form based on the built-in User model
class RegisterForm(forms.ModelForm):
    # 🔐 Password field 1 – renders: <!-- 🔐 Password -->
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Password'  # Sets the text inside the input box
        })
    )

    # 🔐 Password field 2 – renders: <!-- 🔐 Confirm Password -->
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Confirm Password'
        })
    )

    # 👤 First name – renders: <!-- 👥 First + Last Name (side-by-side fields) -->
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'First Name'
        })
    )

    # 👤 Last name – renders: <!-- 👥 First + Last Name (side-by-side fields) -->
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Last Name'
        })
    )

    # 📧 Email – renders: <!-- 📧 Email -->
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Email'
        })
    )

    # 🧾 Username – renders: <!-- 🧾 Username -->
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Username'
        })
    )

    # 📞 Phone (optional) – not shown in HTML yet, ready for future extension
    phone = forms.CharField(
        label="Phone Number",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Phone Number'
        })
    )

    # 🌍 Country (optional) – not shown in HTML yet, ready for future extension
    country = forms.CharField(
        label="Country",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Country'
        })
    )

    # 🏤 Postal Code (optional) – not shown in HTML yet, ready for future extension
    postal_code = forms.CharField(
        label="Postal Code",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'login-dark-input',
            'placeholder': 'Postal Code'
        })
    )

    # 🌐 Language selection – not shown in HTML yet, ready for future extension
    language = forms.ChoiceField(
        label="Preferred Language",
        required=False,
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        widget=forms.Select(attrs={
            'class': 'login-dark-input'  # select dropdown
        })
    )

    class Meta:
        model = User
        # Fields rendered explicitly in the HTML form template
        fields = ('username', 'first_name', 'last_name', 'email')

    # 🔁 Validates that both password fields match
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(sysmsg.MESSAGES["PASSWORD_MISMATCH"])
        return password2

    # 💾 Saves the user with encrypted password – called when form.save() is used in the view
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Encrypt the password
        user.username = self.cleaned_data["username"]
        user.is_active = True  # ✅ Ensure user can login right after registering
        if commit:
            user.save()
        return user

        # GOOGLE CAPTCHA

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # ⬅️ Requests extraction if it comes
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if not self.request:
            return cleaned_data  # ⛔ There isnt request, we dont need validate captcha

        recaptcha_response = self.request.POST.get("g-recaptcha-response")
        if not recaptcha_response:
            self.add_error(None, sysmsg.MESSAGES["CAPTCHA_REQUIRED"])
            return cleaned_data

        # ✅ Validation vs  Google
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        response = requests.post(verify_url, data={
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response,
        })
        result = response.json()

        if not result.get("success"):
            raise forms.ValidationError(sysmsg.MESSAGES["CAPTCHA_INVALID"])

        return cleaned_data        


# Login with email
# -------------------------------
# 📄 File: apps/users/forms.py
# -------------------------------
User = get_user_model()

class EmailLoginForm(AuthenticationForm):
    """
    Custom Login Form using email instead of username.
    Handles reCAPTCHA only after 3 failed attempts.
    """

    def __init__(self, request=None, *args, **kwargs):
        self.request = request  # Store the request object for access in clean()
        super().__init__(request, *args, **kwargs)

    def clean(self):
        """
        Full validation:
        - Check reCAPTCHA (after 3 failed attempts)
        - Check user exists by email
        - Check password
        """
        cleaned_data = super().clean()

        # 🔐 Validate reCAPTCHA if over threshold
        if self.request:
            attempts = self.request.session.get("login_attempts", 0)
            if attempts >= 3:
                recaptcha_response = self.request.POST.get("g-recaptcha-response")
                if not recaptcha_response:
                    raise forms.ValidationError(sysmsg.MESSAGES["CAPTCHA_REQUIRED"])

                response = requests.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": settings.RECAPTCHA_SECRET_KEY,
                        "response": recaptcha_response,
                    }
                )
                if not response.json().get("success"):
                    raise forms.ValidationError(sysmsg.MESSAGES["CAPTCHA_INVALID"])

        # 🔑 Custom email + password check (without backend yet)
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(sysmsg.MESSAGES["LOGIN_FAILED"])

            if not user.check_password(password):
                raise forms.ValidationError(sysmsg.MESSAGES["LOGIN_FAILED"])

            # ✅ Let Django handle 'is_active' (but we will handle 'is_verified' in the View)
            self.confirm_login_allowed(user)

            # 🔗 Store user for later usage in the View (self.user_cache)
            self.user_cache = user

        return self.cleaned_data

    def get_user(self):
        """
        Expose the validated user object.
        """
        return getattr(self, 'user_cache', None)