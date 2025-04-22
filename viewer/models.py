from django.db import models
from django.db.models import CASCADE, CharField, DateTimeField, TextField, DecimalField, ForeignKey, BooleanField
from django.utils import timezone
from django.conf import settings


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
    duration = CharField(max_length=50)
    coach = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='services')
    session_type = ForeignKey(SessionType, on_delete=CASCADE, related_name='services')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.coach.get_full_name()}"


class Session(models.Model):
    client = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='client_sessions')
    coach = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='coach_sessions')
    service = ForeignKey(Service, on_delete=CASCADE, related_name='sessions')
    status = ForeignKey(SessionStatus, on_delete=CASCADE, related_name='sessions')
    scheduled_at = DateTimeField()
    notes = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session with {self.coach.get_full_name()} at {self.scheduled_at}"


class Payment(models.Model):
    session = ForeignKey(Session, on_delete=CASCADE, related_name='payments')
    amount = DecimalField(max_digits=10, decimal_places=2)
    payment_method = ForeignKey(PaymentMethod, on_delete=CASCADE, related_name='payments')
    paid_at = DateTimeField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.session} - {self.amount}"


class Review(models.Model):
    session = ForeignKey(Session, on_delete=CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.session}"
