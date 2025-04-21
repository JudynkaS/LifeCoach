from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from django.db.models import Model, CharField, ForeignKey, CASCADE, DateTimeField, TextField, BooleanField, DecimalField, IntegerField, OneToOneField


class User(AbstractUser):
    """Extended User model"""
    is_client = BooleanField(default=False)
    is_coach = BooleanField(default=False)
    date_joined = DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'viewer'


class SessionType(Model):
    name = CharField(max_length=32, default='Default Session Type')
    code = CharField(max_length=10, default='DEFAULT')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SessionStatus(Model):
    name = CharField(max_length=32, default='Pending')
    code = CharField(max_length=10, default='PENDING')

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Session statuses"

    def __str__(self):
        return self.name


class PaymentMethod(Model):
    name = CharField(max_length=32, default='Cash')
    code = CharField(max_length=10, default='CASH')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Profile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='viewer_profile')
    phone = CharField(max_length=20, null=True, blank=True)
    timezone = CharField(max_length=50, default='UTC')
    bio = TextField(null=True, blank=True)
    preferred_contact = CharField(max_length=20, default='email')
    is_client = BooleanField(default=True)
    is_coach = BooleanField(default=False)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"


class Service(Model):
    name = CharField(max_length=100, default='Default Service')
    description = TextField(null=True, blank=True)
    price = DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration = IntegerField(default=60, help_text="Duration in minutes")
    is_active = BooleanField(default=True)
    currency = CharField(max_length=3, default='USD')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.duration} min)"


class Session(Model):
    client = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='viewer_client_sessions')
    coach = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='viewer_coach_sessions')
    service = ForeignKey(Service, on_delete=CASCADE)
    date_time = DateTimeField(default=datetime.now)
    duration = IntegerField(default=60, help_text="Duration in minutes")
    session_type = ForeignKey(SessionType, on_delete=CASCADE)
    status = ForeignKey(SessionStatus, on_delete=CASCADE)
    notes = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.name} ({self.date_time})"


class Payment(Model):
    session = ForeignKey(Session, on_delete=CASCADE, related_name='payments')
    amount = DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = ForeignKey(PaymentMethod, on_delete=CASCADE)
    status = CharField(max_length=20, default='pending')
    transaction_id = CharField(max_length=100, null=True, blank=True)
    currency = CharField(max_length=3, default='USD')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Payment for {self.session} - {self.amount} {self.currency}"


class Review(Model):
    session = ForeignKey(Session, on_delete=CASCADE, related_name='reviews')
    rating = IntegerField(
        default=5,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Review for {self.session} - {self.rating} stars"
