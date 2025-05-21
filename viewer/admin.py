from django.contrib import admin
from .models import SessionType, SessionStatus, PaymentMethod, Session, Payment, Review
from .models import Category, Service

admin.site.register(Category)


@admin.register(SessionType)
class SessionTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(SessionStatus)
class SessionStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "duration", "price", "coach")
    list_filter = ("coach", "session_type")
    search_fields = ("name", "description", "coach__username")
    raw_id_fields = ("coach",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("service", "client", "coach", "date_time", "status")
    list_filter = ("status", "service", "client", "coach")
    search_fields = ("client__username", "coach__username", "service__name", "notes")
    raw_id_fields = ("client", "coach", "service")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("session", "amount", "payment_method", "paid_at")
    list_filter = ("payment_method", "paid_at")
    search_fields = ("session__client__username", "session__service__name")
    raw_id_fields = ("session", "payment_method")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("session", "rating", "created")
    list_filter = ("rating", "created")
    search_fields = ("session__client__username", "session__coach__username", "comment")
    raw_id_fields = ("session",)
