from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model  # ✅ Import correct model dynamically
# ✅ Used for login via email
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings  # ✅ Access to environment-based settings
import requests
from django.conf import settings
from project_root import messages as sysmsg  # import messages (central messages platform)

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
            raise ValidationError("Passwords do not match.")
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
class EmailLoginForm(AuthenticationForm):
    """
    🔐 Custom login form that enforces reCAPTCHA only after 3 failed login attempts.
    Validates reCAPTCHA BEFORE running Django's default credential check.
    """

    def __init__(self, request=None, *args, **kwargs):
        # 🔗 Attach the request object so we can access session and POST data
        self.request = request
        super().__init__(request, *args, **kwargs)

    def clean(self):
        """
        ✅ Validate reCAPTCHA if needed, then proceed with normal Django credential check.
        """
        if not self.request:
            return super().clean()

        # 📦 Track login attempts from session
        session = self.request.session
        attempts = session.get("login_attempts", 0)

        if attempts >= 3:
            # 🧠 Check if the reCAPTCHA token is present
            recaptcha_response = self.request.POST.get("g-recaptcha-response")

            # 🚫 If not completed, show user-friendly error
            if not recaptcha_response:
                self.add_error(None, sysmsg.MESSAGES["CAPTCHA_REQUIRED"])
                return super().clean()

            # ✅ Validate the token with Google's API
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            response = requests.post(verify_url, data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response,
            })
            result = response.json()

            if not result.get("success"):
                self.add_error(None, sysmsg.MESSAGES["CAPTCHA_INVALID"])
                return super().clean()

        # 🔐 Credentials check (email/password)
        return super().clean()
