from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Creates missing user profiles'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0

        for user in users_without_profile:
            Profile.objects.create(user=user)
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} missing profile(s)'
            )
        ) 