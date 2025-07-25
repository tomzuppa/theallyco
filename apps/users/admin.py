# ✅ Cleaned and Documented admin.py for User Management

# ------------------------
# 📦 Django Admin Imports
# ------------------------
from django.contrib import admin                          # Base admin interface
from django.contrib.auth.admin import UserAdmin           # Full UserAdmin for auth model support
from django.utils.translation import gettext_lazy as _    # Enables i18n for field labels

# ------------------------
# 👤 User and Config Models
# ------------------------
from .models import CustomUser, AuthConfig                # AUTH_USER_MODEL + Google login toggle
from .models import PasswordResetLog   # Log about passwords resets

# ------------------------
# 🧍 CustomUser Admin Configuration
# ------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel interface for CustomUser model.

    Features:
    - Extends Django's UserAdmin
    - Adds new profile fields (avatar, phone, etc.)
    - Organizes fields into logical sections
    - Used to manage users via Django admin
    """

    # 📂 Grouped fields when editing existing users
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'email', 'avatar',
                'phone', 'country', 'postal_code', 'preferred_language'
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Verification'), {'fields': ('is_verified',)}),
    )

    # 📂 Fields shown when creating a new user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'first_name', 'last_name', 'email',
                'phone', 'country', 'postal_code', 'preferred_language'
            ),
        }),
    )

    # 📋 Fields shown in the user list view
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'phone', 'country', 'preferred_language',
        'is_active', 'is_staff', 'is_verified', 'password',
         'terms_accepted'
    )

    # 🔍 Searchable fields in admin UI
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # 🔡 Default sort order
    ordering = ('username',)


# ------------------------
# 🎛️ AuthConfig Admin Toggle (Google Login)
# ------------------------
admin.site.register(AuthConfig)
"""
    Registers the AuthConfig model in admin:
    - Allows enabling/disabling Google login from admin panel
    - Referenced in: views.CustomLoginView
"""


# --------------------------------------------------
# Admin configuration to manage logs (attempts to reset password)
# --------------------------------------------------
# 🛡️ Registers the PasswordResetLog model in Django Admin
@admin.register(PasswordResetLog)
class PasswordResetLogAdmin(admin.ModelAdmin):
    # 🖥️ Columns to display in the admin list view
    list_display = ("email", "successful", "ip_address", "user_agent","device_type", "browser", "os", "timestamp")

    # 🔍 Filters available in the sidebar (for quick filtering)
    list_filter = ("successful", "timestamp")

    # 🔎 Fields that can be searched via the admin search bar
    search_fields = ("email", "ip_address", "user_agent")

    # ⏱️ Default ordering for list view (most recent attempts first)
    ordering = ("-timestamp",)

    # 🔒 Fields that are read-only (no editing allowed through admin UI)
    readonly_fields = ("email", "successful", "ip_address", "user_agent", "timestamp")

    # 🚫 Disables the "Add" button in the admin for this model
    def has_add_permission(self, request):
        return False

    # 🚫 Disables editing of existing entries
    def has_change_permission(self, request, obj=None):
        return False

    # 🚫 Disables deletion of log entries from admin
    def has_delete_permission(self, request, obj=None):
        return False
