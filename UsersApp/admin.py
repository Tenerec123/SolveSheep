from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    readonly_fields = ('last_login', 'last_username_change')
    # Appearance of the "Change User" page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'last_username_change')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Appearance of the "Add User" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Cambiamos password por password1 y confirm_password por password2
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)