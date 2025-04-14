from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class ServiceType(models.TextChoices):
    """Enum for service types"""
    TYPE1 = 'TYPE1', 'Type 1'
    TYPE2 = 'TYPE2', 'Type 2'
    # Add more types as needed

class PaymentMethod(models.TextChoices):
    """Enum for payment methods"""
    PAYPAL = 'PAYPAL', 'PayPal'
    VENMO = 'VENMO', 'Venmo'
    CASH = 'CASH', 'Cash'

class SessionStatus(models.TextChoices):
    """Enum for session status"""
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    PENDING = 'PENDING', 'Pending'

class SessionType(models.TextChoices):
    """Enum for session type"""
    PERSONAL = 'PERSONAL', 'Personal'
    ONLINE = 'ONLINE', 'Online'

class User(AbstractUser):
    """Extended User model"""
    is_client = models.BooleanField(default=False)
    is_coach = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

class Profile(models.Model):
    """User profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    timezone = models.CharField(max_length=50)
    bio = models.TextField()
    preferred_contact = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Service(models.Model):
    """Service model"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # in minutes
    is_active = models.BooleanField(default=True)
    service_type = models.CharField(
        max_length=20,
        choices=ServiceType.choices,
        default=ServiceType.TYPE1
    )

    def __str__(self):
        return self.name

class Session(models.Model):
    """Session model"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_sessions')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach_sessions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    duration = models.IntegerField()  # in minutes
    type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.PERSONAL
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.PENDING
    )
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session: {self.client.username} with {self.coach.username} on {self.date_time}"

class Payment(models.Model):
    """Payment model"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PAYPAL
    )
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment: {self.amount} for session {self.session.id}"

class Review(models.Model):
    """Review model"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for session {self.session.id}: {self.rating}/5" 