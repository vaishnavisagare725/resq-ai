import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

REQUIRED = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']

RECOMMENDED = {
    'DB_SSL_CA': 'managed databases such as Aiven need TLS',
    'CLOUDINARY_URL': 'without it, uploaded photos are lost when the server restarts',
    'CSRF_TRUSTED_ORIGINS': 'the Django admin login fails over https without it',
    'CORS_ALLOWED_ORIGINS': 'the website cannot call the API without it',
    'ADMIN_USERNAME': 'no admin account will be created',
    'ADMIN_PASSWORD': 'no admin account will be created',
    'DEMO_PASSWORD': 'no demo accounts will be created',
}


class Command(BaseCommand):
    help = 'Check that the environment variables a deployment needs are set (names only, never values).'
    requires_system_checks = []   # this command must not touch the database

    def handle(self, *args, **options):
        problems = [f'{name} is not set' for name in REQUIRED if not os.getenv(name)]
        if not settings.DEBUG and os.getenv('DB_HOST') in ('localhost', '127.0.0.1'):
            problems.append('DB_HOST is "localhost", which is this container itself, not your database')

        for name, why in RECOMMENDED.items():
            if not os.getenv(name):
                self.stdout.write(self.style.WARNING(f'not set: {name} ({why})'))

        if problems:
            raise CommandError('Missing or wrong settings:\n  - ' + '\n  - '.join(problems))
        self.stdout.write(self.style.SUCCESS('Environment looks fine.'))