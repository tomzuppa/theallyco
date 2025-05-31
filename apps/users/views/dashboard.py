# -----------------------------------------
# 🛡️ DASHBOARD VIEW (Protected)
# -----------------------------------------

# 📦 Core Django Modules
from django.shortcuts import render                 # Used to render templates
from django.contrib.auth.decorators import login_required  # Protects views for authenticated users
from datetime import datetime                       # Utility to get current time

# 🔐 Protected dashboard view
@login_required
def dashboard_base(request):
    """
    🛡️ Displays the main dashboard (protected).
    - Requires user to be logged in.
    - Passes the current date and username to the template.

    Template:
    - 'dashboardb/dashboardb.html'
    """
    current_date = datetime.now().strftime("%b %d, %Y")  # E.g., "May 22, 2025"
    user_name = request.user.username                    # Logged-in user's username

    context = {
        'current_date': current_date,
        'username': user_name
    }

    return render(request, 'dashboardb/dashboardb.html', context)
