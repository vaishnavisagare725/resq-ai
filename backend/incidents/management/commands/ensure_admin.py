import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create the site admin from ADMIN_USERNAME and ADMIN_PASSWORD, if it does not exist yet.'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')
        if not username or not password:
            self.stdout.write('ADMIN_USERNAME or ADMIN_PASSWORD is not set: no admin created.')
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Admin {username} already exists.')
            return
        User.objects.create_superuser(
            username=username, email=os.getenv('ADMIN_EMAIL', ''), password=password, role='admin'
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin {username}.'))