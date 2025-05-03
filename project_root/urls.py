from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect empty root to login
    path('', lambda request: redirect('users:login')),

    # Users app (login/logout/dashboard)
    path('users/', include('apps.users.urls')),
]
