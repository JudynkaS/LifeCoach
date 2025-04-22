from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_client', 'is_coach', 'is_staff')
    list_filter = ('is_client', 'is_coach', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Roles', {'fields': ('is_client', 'is_coach')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_client', 'is_coach'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'timezone', 'preferred_contact', 'is_client', 'is_coach')
    list_filter = ('is_client', 'is_coach', 'timezone')
    search_fields = ('user__username', 'user__email', 'phone', 'bio')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'phone', 'timezone', 'preferred_contact')}),
        ('Additional Info', {'fields': ('bio',)}),
        ('Roles', {'fields': ('is_client', 'is_coach')}),
    )
    ordering = ('user__username',)
