
# urls.py inside the users app
from django.urls import path
from .views import CustomLoginView  # ✅ Make sure this exists

app_name = 'users'  # ✅ Required for namespacing

urlpatterns = [
    # ✅ URL PATTERNS
    path('login/', CustomLoginView.as_view(), name='login'),
]
