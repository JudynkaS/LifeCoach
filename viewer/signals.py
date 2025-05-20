from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Session

@receiver(post_save, sender=Session)
def notify_session_created(sender, instance, created, **kwargs):
    """Pošle notifikaci při vytvoření nové rezervace"""
    if created:
        subject = 'Nová rezervace'
        message = f'Byla vytvořena nová rezervace na {instance.date_time}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.client.email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
        )

@receiver(post_save, sender=Session)
def notify_session_status_change(sender, instance, **kwargs):
    """Pošle notifikaci při změně stavu rezervace"""
    if not kwargs.get('created'):  # Pokud se nejedná o novou rezervaci
        subject = 'Změna stavu rezervace'
        message = f'Stav vaší rezervace na {instance.date_time} byl změněn na {instance.status}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.client.email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
        ) 