# ---------------------------------------------
# 🔗 users/urls.py - Routes for user operations
# ---------------------------------------------

# 🛠️ Django Core URL handler
from django.urls import path

# 📦 Views for authentication and account flows
from apps.users import views
from .views import RegisterTokenView          # 📥 Class-based view for email + token registration
from .views import TermsView                   # 📜 Static Terms and Conditions page
from .views.register import check_token_status  
from apps.users.views.reset_pass import CustomPasswordResetView
from apps.users.views.reset_pass_confirm import CustomPasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView
from django.contrib.auth import views as auth_views
# En la parte superior del archivo, donde tienes los otros imports



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

    # 🔁 Password Reset Flow
    # ------------------------------------------

    # 📩 1. Request password reset form (user submits email)
    path('reset-password/'
    , CustomPasswordResetView.as_view(
        template_name='users/password_reset_form.html'
    ), name='password_reset'),

    # 📤 2. Confirmation page: "We sent an email"
    path('reset-password/done/'
    , PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    # 🔐 3. Link from email: form to set a new password
    path(
        'reset/<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(
            # Personalized template
            template_name='users/password_reset_confirm.html'
        ),name='password_reset_confirm'),

    # ✅ 4. Final confirmation: "Your password has been changed"
    path('reset-password/complete/'
    , PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    #JSON to get confirmation about the expiration of the token
    path('register/check-status/', check_token_status, name='check_token_status')

]
