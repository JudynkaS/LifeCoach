from django.db import models
from django.db.models import CASCADE, CharField, DateTimeField, TextField, DecimalField, ForeignKey, BooleanField
from django.utils import timezone
from django.conf import settings
from accounts.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy


class SessionType(models.Model):
    name = CharField(max_length=100)
    description = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SessionStatus(models.Model):
    name = CharField(max_length=50)
    description = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = CharField(max_length=50)
    description = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = CharField(max_length=100)
    description = TextField()
    price = DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # in minutes
    is_active = BooleanField(default=True)
    currency = CharField(max_length=3, default='USD')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    coach = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='services')
    session_type = ForeignKey('viewer.SessionType', on_delete=CASCADE, related_name='services')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.coach.get_full_name()}"


class Session(models.Model):
    SESSION_TYPES = [
        ('online', 'Online'),
        ('personal', 'Personal'),
    ]
    
    SESSION_STATUS = [
        ('CANCELLED', 'Cancelled'),
        ('CONFIRMED', 'Confirmed'),
        ('CHANGED', 'Changed'),
    ]

    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='client_sessions')
    coach = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='coach_sessions')
    service = models.ForeignKey('viewer.Service', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    duration = models.IntegerField(default=60)  # default duration 60 minutes
    type = models.CharField(max_length=10, choices=SESSION_TYPES, default='online')  # default to online sessions
    status = models.CharField(max_length=10, choices=SESSION_STATUS, default='CONFIRMED')
    notes = models.TextField(blank=True, null=True)  # make notes optional
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.service.name} with {self.coach} on {self.date_time}"

    @property
    def is_past(self):
        return self.date_time < timezone.now()

    @property
    def can_cancel(self):
        """Session can be cancelled more than 24 hours in advance"""
        if self.status != 'CONFIRMED':
            return False
        return (self.date_time - timezone.now()).total_seconds() > 24 * 60 * 60


class Payment(models.Model):
    session = ForeignKey('viewer.Session', on_delete=CASCADE, related_name='payments')
    amount = DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey('viewer.PaymentMethod', on_delete=models.CASCADE)
    paid_at = DateTimeField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.session} - {self.amount}"


class Review(models.Model):
    session = ForeignKey('viewer.Session', on_delete=CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.session}"

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

