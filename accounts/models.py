from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


class User(AbstractUser):
    """Extended User model"""
    is_client = models.BooleanField(default=False)
    is_coach = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'accounts'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    bio = models.TextField(null=True, blank=True)
    preferred_contact = models.CharField(max_length=20, default='email')
    is_client = models.BooleanField(default=True)
    is_coach = models.BooleanField(default=False)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        app_label = 'accounts'

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"
