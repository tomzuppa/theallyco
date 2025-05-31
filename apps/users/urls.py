# ---------------------------------------------
# 🔗 users/urls.py - Routes for user operations
# ---------------------------------------------

# 🛠️ Django Core URL handler
from django.urls import path

# 📦 Views for authentication and account flows
from apps.users import views
from .views import RegisterTokenView  # 📥 Class-based view for email + token registration
from .views import TermsView
# 🔖 App namespace
app_name = 'users'

# 🚏 Route definitions for user management
urlpatterns = [
    # 🔐 Login page (email + password)
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # 🚪 Logout endpoint
    path('logout/', views.logout_view, name='logout'),

    # 📝 Register with token verification (2-step flow)
    path('register/', RegisterTokenView.as_view(), name='register'),

    # ⛔ Shown if user exceeded allowed attempts or is blocked
    path('blocked/', views.BlockedView.as_view(), name='blocked'),

    # 📊 Default dashboard after login
    path('dashboard/', views.dashboard_base, name='dashboard'),

    # 📃 Static Terms and Conditions page
    path("terms/", TermsView.as_view(), name="terms"),

    # 🌐 Google Login endpoint (triggers OAuth flow)
    path('login/google/', views.google_login, name='google_login'),

    

    # 🔴 [DEPRECATED] Account activation via email link (no longer used)
    # path('activate/', views.activate_account, name='activate_account'),

    # ✅ Optional: Manual token verification fallback (if separate from register)
    #path('verify-account/', views.VerifyAccountView.as_view(), name='verify_account'),

    # 🔧 [Optional] OAuth callback handler (used for manual Google OAuth2, if needed)
    # path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
]

