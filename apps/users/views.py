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


# ----------------------------
# Login process (app users)
# ----------------------------
class CustomLoginView(LoginView):
    """
    Custom login view using Django's built-in LoginView.
    - Uses our custom template located at 'users/login.html'
    - Redirects authenticated users if they try to access login again
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True

# ----------------------------
# views.py in users app
# ----------------------------
# ✅ Logs the user out and redirects to login page
def logout_view(request):
    logout(request)
    return redirect('users:login')


# ✅ Displays the base dashboard (placeholder version)
@login_required
def dashboard_base(request):
    context = {'current_date': datetime.now().strftime("%b %d, %Y"),  # Example: Apr 18, 2025
    }
    return render(request, 'dashboardb.html', context)


# 🧭 Class-based view for user registration
class RegisterView(FormView):
    template_name = "users/register.html"           # 📄 Template path
    form_class = RegisterForm                       # 📋 Form class to render and validate
    success_url = reverse_lazy('users:login')       # ✅ Redirect after successful registration

    def form_valid(self, form):
        """
        If the form is valid, save the new user.
        You can also handle additional profile data here in the future.
        """
        form.save()
        messages.success(self.request, "Your account has been created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, show error messages.
        """
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)