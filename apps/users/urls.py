# 📍 urls.py inside the users app
# Defines the route mappings for login, logout, registration, dashboard, etc.

# 🛣️ Core Django module for declaring URL routes
from django.urls import path

# 🔧 Direct view imports for class-based and function-based views
# Impacts: Used for routing to custom login, logout, and registration logic
from .views import CustomLoginView, logout_view, RegisterView

# 🔁 Import full views module to access additional function-based views
# Impacts: Required to reference views like dashboard_base, terms, google_login
import apps.users.views as views



# 🧭 Namespace for the users app, enables calling URLs with 'users:<name>' pattern
app_name = 'users'

urlpatterns = [
    # 🔐 Login page (Custom class-based view with reCAPTCHA and email support)
    path('login/', CustomLoginView.as_view(), name='login'),

    # 🚪 Logout handler (supports auto-logout messaging)
    path('logout/', views.logout_view, name='logout'),

    # 🧾 User registration page (CustomRegisterForm + reCAPTCHA + email validation)
    path('register/', RegisterView.as_view(), name='register'),

    # 🖥️ Main user dashboard (protected view shown post-login)
    path('dashboard/', views.dashboard_base, name='dashboard'),

    # 📄 Terms and Conditions page (linked from registration form)
    path('terms/', views.terms, name='terms'),

    # 🌐 Google OAuth2 login (redirects to Google's consent screen)
    path('login/google/', views.google_login, name='google_login'),

    # 🔗 Used by reverse('users:activate_account') -- Token for mail validation
    path('activate/', views.activate_account, name='activate_account'),

]

