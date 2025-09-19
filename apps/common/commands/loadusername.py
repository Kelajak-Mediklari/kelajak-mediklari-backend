from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Loads regions if they are not loaded"

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not user.username:
                user.username = f"{user.phone_number}_{user.type}"
                user.save(update_fields=['username'])
