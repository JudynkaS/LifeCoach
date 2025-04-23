from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    preferred_contact = models.CharField(max_length=20, blank=True)
    is_client = models.BooleanField(default=False)
    is_coach = models.BooleanField(default=False)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return self.user.username

    def __repr__(self):
        return f"Profile(user={self.user})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance for all newly created User instances."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save Profile instance for all saved User instances."""
    instance.profile.save()


