from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from datetime import datetime
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib import messages
from .forms import EmailLoginForm # ✅ authentication.py
from project_root import messages as sysmsg  # import messages (central messages platform)
from django.conf import settings  # ✅ Required to access .env variables like RECAPTCHA keys
import requests  # ✅ Required to validate reCAPTCHA with Google's API

# ------------------------------------------------------------------------------
# 🔑 Custom LoginView with reCAPTCHA and 'Keep me signed in' functionality
# ------------------------------------------------------------------------------
class CustomLoginView(LoginView):
    """
    🔐 Custom login view with conditional reCAPTCHA and 'Keep me signed in' support.
    The form (EmailLoginForm) handles reCAPTCHA validation based on failed attempts.
    """
    template_name = 'users/login.html'
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        """
        🎯 Add reCAPTCHA public key and condition flag to context (used by template).
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY
        context["show_recaptcha"] = self.request.session.get("login_attempts", 0) >= 3
        return context

    def get_form_kwargs(self):
        """
        🔄 Pass the request to the form so it can access session (used for reCAPTCHA logic).
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        """
        ✅ Login succeeded: reset login attempts, set session duration, show success message.
        """
        self.request.session["login_attempts"] = 0

        # 💾 Handle "Keep me signed in" option
        remember = self.request.POST.get('remember')
        self.request.session.set_expiry(60 * 60 * 24 * 30 if remember else 0)

        messages.success(self.request, sysmsg.MESSAGES["LOGIN_SUCCESS"])
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        ❌ Login failed: increase login attempts and show failure message.
        CAPTCHA validation is handled inside the form itself.
        """
        self.request.session["login_attempts"] = self.request.session.get("login_attempts", 0) + 1

        print("Login attempts:", self.request.session.get("login_attempts", 0))  # 👈 For debugging
         
        # messages.error(self.request, sysmsg.MESSAGES["LOGIN_FAILED"])
        return super().form_invalid(form)

    def get_success_url(self):
        """
        📍 Redirect path after successful login.
        """
        return reverse_lazy('users:dashboard')



# ----------------------------
# views.py in users app
# ----------------------------
# 🔐 Logs out the user and redirects to login page
def logout_view(request):
    # 🚪 Terminates the current session and logs out the user
    logout(request)

    # 🧠 Check if the logout was triggered by inactivity
    # 'auto=1' comes from the frontend (auto_logout.js)
    if request.GET.get("auto") == "1":
        # 📩 Show a specific message indicating auto-logout due to inactivity
        messages.warning(request, sysmsg.MESSAGES["AUTO_LOGOUT_WARNING"])
    else:
        # ✅ Normal logout initiated by the user
        messages.success(request, sysmsg.MESSAGES["LOGOUT_SUCCESS"])

    # 🔁 Redirect to login page after logout
    return redirect('users:login')



# ✅ Displays the base dashboard (placeholder version)
# 🛡️ Requires the user to be authenticated
@login_required
def dashboard_base(request):
    # 📅 Create context with current date formatted as: "Apr 18, 2025"
    current_date = datetime.now().strftime("%b %d, %Y")

    # 🧑‍💼 Get the username of the currently logged-in user
    user_name = request.user.username

    # 📦 Bundle the context data into a dictionary to pass to the template
    context = {
        'current_date': current_date,
        'username': user_name
    }

    # 🎨 Render the dashboard template and inject the context variables
    return render(request, 'dashboardb/dashboardb.html', context)



# 🧭 Class-based view for user registration
class RegisterView(FormView):
    template_name = "users/register.html"           # 📄 Template path
    form_class = RegisterForm                       # 📋 Form class to render and validate
    success_url = reverse_lazy('users:login')       # ✅ Redirect after successful registration

    def get_context_data(self, **kwargs):
        """
        Add the reCAPTCHA site key to the context so it can be used in the template.
        """
        context = super().get_context_data(**kwargs)
        context["recaptcha_site_key"] = settings.RECAPTCHA_SITE_KEY  # 🔑 Loaded from .env
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the new user.
        You can also handle additional profile data here in the future.
        """
        form.save()
        messages.success(self.request, sysmsg.MESSAGES["REGISTER_SUCCESS"])  # 👈 Message of registration sucess
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, show error messages.
        """
        #messages.error(self.request, sysmsg.MESSAGES["GENERIC_ERROR"])  # 👈 Message of error
        return super().form_invalid(form)
    
    # Google captcha
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # ✅ Here the info is sent
        return kwargs        

"""
Terms and Conditions for Registration Page
"""
def terms(request):
    return render(request, 'legal/terms.html')