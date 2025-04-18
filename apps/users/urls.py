
# urls.py inside the users app
from django.urls import path
from .views import CustomLoginView  # ✅ Custom class-based view
import apps.users.views as views     # ✅ Add this to access logout_view and dashboard_base


app_name = 'users'  # ✅ Required for namespacing

urlpatterns = [
    # ✅ URL PATTERNS
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  # LogOut
]
