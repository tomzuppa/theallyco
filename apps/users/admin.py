from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, AuthConfig

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for managing CustomUser fields.
    """

    # 🧾 Field groups shown when editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'email', 'avatar',
                'phone', 'country', 'postal_code', 'preferred_language'  # 🆕 New fields
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Verification'), {'fields': ('is_verified',)}),
    )

    # 🪪 Fields shown when creating a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'first_name', 'last_name', 'email',
                'phone', 'country', 'postal_code', 'preferred_language'  # 🆕 New fields
            ),
        }),
    )

    # 📋 Displayed in the user list table
    list_display = (
    'username', 'email', 'first_name', 'last_name',
    'phone', 'country', 'preferred_language',
    'is_active',     # ✅ ← AÑADIDO
    'is_staff',
    'is_verified',
    'password'
)

    # 🔍 Fields searchable from the admin search box
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # 🔡 Default sorting of the user list
    ordering = ('username',)



"""-----------------------------------------------------------------------
ENABLE O DISABLE GOOGLE LOGIN BUTTON IN THE LOGIN PAGE FROM ADMIN PANEL
-------------------------------------------------------------------------"""
admin.site.register(AuthConfig)