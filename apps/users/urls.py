
# urls.py inside the users app
from django.urls import path
from .views import CustomLoginView, logout_view, RegisterView  # ✅ Custom class-based view
import apps.users.views as views     # ✅ Add this to access logout_view and dashboard_base


app_name = 'users'  # ✅ Required for namespacing

urlpatterns = [
    # ✅ URL PATTERNS
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  # LogOut
    path('register/', RegisterView.as_view(), name='register'),  #New User Register
    path('dashboard/', views.dashboard_base, name='dashboard'), #main dashboard
    path('terms/', views.terms, name='terms'), #Terms and conditions (for registration)
    path('login/google/', views.google_login, name='google_login'), #Google login

]
