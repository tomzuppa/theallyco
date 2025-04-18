from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from datetime import datetime

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
