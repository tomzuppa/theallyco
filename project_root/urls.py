
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Routes for login/logout/etc (app users)
    path('users/', include('apps.users.urls')),

    # Redirect empty root path to login page
    path('', lambda request: redirect('users:login')),
]