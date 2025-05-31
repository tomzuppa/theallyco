# -------------------------------------------------------------------------------------------
# 📝 users/views/register.py — Token-based Registration View with Email Verification
# -------------------------------------------------------------------------------------------

# 🧠 Core Django imports
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core import signing
from django.conf import settings
from django.contrib.auth import get_user_model

# 📄 Form and custom messages
from ..forms import RegisterForm
from project_root import messages as sysmsg  # 📁 External system messages (used in all views)

# 📧 Mail utility for sending verification tokens
from ..utils.emails import send_activation_email_from_token

# 🧍‍♂️ Dynamic user model
User = get_user_model()

# ⏲️ Token expiration limit
TOKEN_EXPIRY = settings.ACTIVATION_TOKEN_EXPIRY


# ✨ DRY helper to render register form with token support
# Impacts: register_token.html

def render_register(request, form, **kwargs):
    return render(request, "users/register_token.html", {
        "form": form,
        "show_token_field": kwargs.get("show_token_field", False),
        "disable_fields": kwargs.get("disable_fields", False),
        "countdown": kwargs.get("countdown", 0),
        "token_expired": kwargs.get("token_expired", False),
        "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY  # ✅ Key to  HTML
    })


class RegisterTokenView(View):
    """
    🗺️ Handles user registration in two steps:
    1. Form submission & token generation
    2. Token verification & user creation

    Impacts:
    - Frontend: register_token.html (reCAPTCHA, token input, blocking fields)
    - Email flow: utils/emails.py (token delivery)
    - Session keys: store state between steps
    """

    def get(self, request, *args, **kwargs):
        step = request.session.get("register_step", "form")
        form_data = request.session.get("register_user_data")
        form = RegisterForm(initial=form_data) if form_data else RegisterForm()

        return render_register(request, form,
                               show_token_field=step == "verify",
                               disable_fields=step == "verify",
                               countdown=TOKEN_EXPIRY if step == "verify" else 0)

    def post(self, request):
        step = request.session.get("register_step", "form")

        if "resend" in request.POST:
            return self._handle_resend(request)

        if step == "form":
            return self._handle_form(request)

        if step == "verify":
            return self._handle_verify(request)

        if step == "blocked":
            return redirect("users:blocked")

        return redirect("users:register")

    def _handle_resend(self, request):
        resend_count = request.session.get("register_resend_count", 0)
        if resend_count >= 3:
            request.session["register_step"] = "blocked"
            messages.error(request, sysmsg.MESSAGES["RESEND_LIMIT_EXCEEDED"])
            return redirect("users:blocked")

        part_a = request.session.get("register_token_part_a")
        part_b = request.session.get("register_token_part_b")

        if not (part_a and part_b):
            messages.error(request, sysmsg.MESSAGES["SESSION_EMAIL_MISSING"])
            return redirect("users:register")

        try:
            user_data = signing.loads(part_a + part_b, salt="register-salt")
            send_activation_email_from_token(user_data["email"], request, part_b)
            request.session["register_resend_count"] = resend_count + 1
            messages.success(request, sysmsg.MESSAGES["ACTIVATION_RESENT"])
        except signing.BadSignature:
            messages.error(request, sysmsg.MESSAGES["INVALID_TOKEN"])

        form_data = request.session.get("register_user_data")
        form = RegisterForm(initial=form_data) if form_data else RegisterForm()
        return render_register(request, form, show_token_field=True, disable_fields=True, countdown=TOKEN_EXPIRY)


    def _handle_form(self, request):
        form = RegisterForm(request.POST)

        # 🔒 Validate Google reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        recaptcha_success = False

        if recaptcha_response:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            })
            result = r.json()
            recaptcha_success = result.get('success', False)

        if not recaptcha_success:
            # ⚠️ User did not pass the CAPTCHA
            messages.error(request, sysmsg.MESSAGES["CAPTCHA_REQUIRED"])
            return render_register(request, form)

        # 📋 If the form is invalid, re-render with errors
        if not form.is_valid():
            return render_register(request, form)

        # 📦 Store form data in session
        data = form.cleaned_data
        request.session["register_user_data"] = data

        # 🔐 Create and split signed token
        token = signing.dumps(data, salt="register-salt")
        part_a, part_b = token[:-15], token[-15:]

        # 💾 Save parts and state in session
        request.session.update({
            "register_token_part_a": part_a,
            "register_token_part_b": part_b,
            "register_step": "verify",
            "register_attempts": 0,
            "register_resend_count": 0
        })

        # 📧 Send part B of token by email
        send_activation_email_from_token(data["email"], request, part_b)

        # ✅ Show message and switch to token input step
        messages.info(request, sysmsg.MESSAGES["ACTIVATION_INSTRUCTIONS"])

        return render_register(request, form, show_token_field=True, disable_fields=True, countdown=TOKEN_EXPIRY)

    def _handle_verify(self, request):
        code = request.POST.get("verification_code")
        form_data = request.session.get("register_user_data")
        form = RegisterForm(initial=form_data) if form_data else RegisterForm()

        if not code:
            messages.error(request, sysmsg.MESSAGES["ACTIVATION_TOKEN_REQUIRED"])
            return render_register(request, form, show_token_field=True, disable_fields=True, token_expired=True)

        attempts = request.session.get("register_attempts", 0)
        if attempts >= 3:
            request.session["register_step"] = "blocked"
            messages.error(request, sysmsg.MESSAGES["RESEND_LIMIT_EXCEEDED"])
            return redirect("users:blocked")

        token = request.session.get("register_token_part_a", "") + code

        try:
            data = signing.loads(token, max_age=TOKEN_EXPIRY, salt="register-salt")

            User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password1"],
                is_verified=True
            )

            request.session.flush()
            messages.success(request, sysmsg.MESSAGES["ACTIVATION_SUCCESS"])
            return redirect("users:login")

        except signing.SignatureExpired:
            messages.error(request, sysmsg.MESSAGES["TOKEN_EXPIRED"])

        except signing.BadSignature:
            messages.error(request, sysmsg.MESSAGES["INVALID_TOKEN"])

        request.session["register_attempts"] = attempts + 1
        return render_register(request, form, show_token_field=True, disable_fields=True, token_expired=True)

