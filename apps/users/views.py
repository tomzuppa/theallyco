from django.shortcuts import render
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    """
    Custom login view using Django's built-in LoginView.
    - Uses our custom template located at 'users/login.html'
    - Redirects authenticated users if they try to access login again
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True

