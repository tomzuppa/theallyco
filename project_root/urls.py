from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from apps.users import views as user_views  # helpful for google login

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect empty root to login
    path('', lambda request: redirect('users:login')),

    # Users app (login/logout/dashboard)
    path('users/', include('apps.users.urls')),

    path('oauth2callback/', user_views.oauth2callback, name='oauth2callback'), #Google login callback
]
