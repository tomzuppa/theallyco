# 📍 urls.py inside the users app
# -------------------------------------------------------
# Defines all user-related routes:
# - Login/logout with custom views
# - Registration and dashboard access
# - Email/token activation and Google OAuth2 login
# - Centralized verification view (2FA style)
# - Terms and blocked user page
# -------------------------------------------------------

# 🛣️ Django URL routing system
from django.urls import path

# 🔧 Class-based views (CBV)
from .views import CustomLoginView, RegisterView, VerifyAccountView, BlockedView

# 🔧 Function-based views (FBV)
from . import views  # Includes: logout_view, dashboard_base, terms, activate_account, google_login

# 🧭 Namespace to allow reverse('users:route_name')
app_name = 'users'

# 🌐 Route definitions
urlpatterns = [

    # 🔐 Login with email + reCAPTCHA
    path('login/', CustomLoginView.as_view(), name='login'),

    # 🚪 Logout endpoint (also used by auto-logout script)
    path('logout/', views.logout_view, name='logout'),

    # 🧾 Registration page (includes email verification & token generation)
    path('register/', RegisterView.as_view(), name='register'),

    # 🖥️ User dashboard (requires login)
    path('dashboard/', views.dashboard_base, name='dashboard'),

    # 📄 Terms and conditions page
    path('terms/', views.terms, name='terms'),

    # 🌐 Google login redirect (starts OAuth2 flow)
    path('login/google/', views.google_login, name='google_login'),

    # 🔗 Email-based token activation (e.g., from email link)
    path('activate/', views.activate_account, name='activate_account'),

    # 🔁 2FA-style token entry & resend page (central verification hub)
    path('verify-account/', VerifyAccountView.as_view(), name='verify_account'),

    # 🚫 Blocked users (after exceeding max resend attempts)
    path('blocked/', BlockedView.as_view(), name='blocked'),
]
