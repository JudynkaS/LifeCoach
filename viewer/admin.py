from django.contrib import admin
from .models import (
    SessionType, SessionStatus, PaymentMethod,
    Profile, Service, Session, Payment, Review
)

@admin.register(SessionType)
class SessionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(SessionStatus)
class SessionStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'timezone', 'is_client', 'is_coach')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('is_client', 'is_coach')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'duration', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'currency')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('client', 'coach', 'service', 'date_time', 'duration', 'status')
    search_fields = ('client__username', 'coach__username', 'service__name')
    list_filter = ('status', 'session_type')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('session', 'amount', 'currency', 'status', 'created')
    search_fields = ('session__client__username', 'transaction_id')
    list_filter = ('status', 'payment_method')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('session', 'rating', 'created')
    search_fields = ('session__client__username', 'comment')
    list_filter = ('rating',)
