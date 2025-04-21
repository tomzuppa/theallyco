from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# 🧾 Custom registration form based on the built-in User model
class RegisterForm(forms.ModelForm):
    # Password fields
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'login-dark-input'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'login-dark-input'})
    )

    # Personal details
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'login-dark-input'})
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={'class': 'login-dark-input'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'login-dark-input'})
    )

    username = forms.CharField(  # Explicitly added to apply styling
        label="Username",
        widget=forms.TextInput(attrs={'class': 'login-dark-input'})
    )

    # Extra fields for profile extension
    phone = forms.CharField(
        label="Phone Number",
        required=False,
        widget=forms.TextInput(attrs={'class': 'login-dark-input'})
    )

    country = forms.CharField(
        label="Country",
        required=False,
        widget=forms.TextInput(attrs={'class': 'login-dark-input'})
    )

    postal_code = forms.CharField(
        label="Postal Code",
        required=False,
        widget=forms.TextInput(attrs={'class': 'login-dark-input'})
    )

    language = forms.ChoiceField(
        label="Preferred Language",
        choices=[('en', 'English'), ('es', 'Español'), ('fr', 'Français')],
        widget=forms.Select(attrs={'class': 'login-dark-input'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    # Validate that both password fields match
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    # Save user with encrypted password and email as username if needed
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data["username"]
        if commit:
            user.save()
        return user
