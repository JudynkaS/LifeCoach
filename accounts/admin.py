from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import pytz

from accounts.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone', 'get_is_coach', 'get_is_client', 'get_is_admin')
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

    def get_is_admin(self, instance):
        return instance.profile.is_admin
    get_is_admin.short_description = 'Admin'
    get_is_admin.boolean = True

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'phone', 'get_timezone_display', 'is_coach', 'is_client', 'is_admin', 'preferred_contact', 'get_city_state')
    list_filter = ('is_coach', 'is_client', 'is_admin', 'timezone', 'city', 'state')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone', 'bio', 'city', 'state')
    raw_id_fields = ('user',)
    readonly_fields = ('user',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'timezone', 'preferred_contact')
        }),
        ('Role', {
            'fields': ('is_coach', 'is_client', 'is_admin')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'sex', 'marital_status', 'occupation', 'street_address', 'city', 'state', 'zip_code')
        }),
        ('Additional Information', {
            'fields': ('bio', 'notifications_enabled', 'avatar'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'

    def get_city_state(self, obj):
        if obj.city and obj.state:
            return f"{obj.city}, {obj.state}"
        return "-"
    get_city_state.short_description = 'Location'

    def get_timezone_display(self, obj):
        try:
            tz = pytz.timezone(obj.timezone)
            now = pytz.datetime.datetime.now(tz)
            # Získání popisu časového pásma
            tzname = tz.tzname(now)
            # Pokus o srozumitelný popis
            tzdesc = tz._tzname if hasattr(tz, '_tzname') and tz._tzname else tz.zone.replace('_', ' ')
            # Pokud je k dispozici oficiální popis v pytz.common_timezones, použijeme jej
            pretty = tz.zone.replace('_', ' ')
            return f"{obj.timezone} ({now.strftime('%z')}) – {tzname if tzname else pretty}"
        except Exception:
            return obj.timezone
    get_timezone_display.short_description = 'Timezone'
    get_timezone_display.admin_order_field = 'timezone'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)