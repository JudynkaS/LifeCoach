from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Vytvoří profil automaticky při vytvoření uživatele"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Uloží profil při uložení uživatele"""
    instance.profile.save()

@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """Smaže profil při smazání uživatele"""
    if hasattr(instance, 'profile'):
        instance.profile.delete() 