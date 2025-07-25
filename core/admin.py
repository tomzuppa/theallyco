from django.contrib import admin
from .models import SignupBranding
# --------------------------------------------------
# Admin configuration to manage SignupBranding from Django admin panel
# --------------------------------------------------
@admin.register(SignupBranding)
class SignupBrandingAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle")  # 🧭 Displayed columns in admin list

