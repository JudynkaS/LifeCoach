from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from accounts.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone', 'get_is_coach', 'get_is_client')
    list_select_related = ('profile',)

    def get_phone(self, instance):
        return instance.profile.phone
    get_phone.short_description = 'Phone'

    def get_is_coach(self, instance):
        return instance.profile.is_coach
    get_is_coach.short_description = 'Coach'
    get_is_coach.boolean = True

    def get_is_client(self, instance):
        return instance.profile.is_client
    get_is_client.short_description = 'Client'
    get_is_client.boolean = True

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'phone', 'timezone', 'is_coach', 'is_client', 'preferred_contact')
    list_filter = ('is_coach', 'is_client', 'timezone')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone', 'bio')
    raw_id_fields = ('user',)
    readonly_fields = ('user',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'timezone', 'preferred_contact')
        }),
        ('Role', {
            'fields': ('is_coach', 'is_client')
        }),
        ('Additional Information', {
            'fields': ('bio', 'notifications_enabled', 'avatar'),
            'classes': ('collapse',)
        }),
    )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'user__first_name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'user__last_name'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)