import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from incidents.ai_service import predict
from incidents.models import CATEGORY_TO_DEPARTMENT, Incident

DEMO_USERS = [
    ('demo_citizen', 'citizen', ''),
    ('demo_fire_responder', 'responder', 'fire'),
    ('demo_medical_responder', 'responder', 'medical'),
    ('demo_fire_worker', 'worker', 'fire'),
    ('demo_medical_worker', 'worker', 'medical'),
]

DEMO_REPORTS = [
    ('Building fire', 'Fire on the second floor, people trapped', 18.5204, 73.8567),
    ('Chest pain', 'Man has severe chest pain at the bus stop', 18.5018, 73.8636),
    ('Water logging', 'Street flooded after heavy rain near the market', 18.5308, 73.8475),
    ('Pothole', 'There is a big pothole on the main road', 18.5114, 73.8265),
]


class Command(BaseCommand):
    help = 'Create demo accounts (password from DEMO_PASSWORD) and sample reports. Safe to run twice.'

    def handle(self, *args, **options):
        password = os.getenv('DEMO_PASSWORD')
        if not password:
            self.stdout.write('DEMO_PASSWORD is not set: no demo data created.')
            return

        User = get_user_model()
        created = 0
        for username, role, department in DEMO_USERS:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username, password=password, role=role, department=department
                )
                created += 1

        if not Incident.objects.exists():
            citizen = User.objects.get(username='demo_citizen')
            for title, description, latitude, longitude in DEMO_REPORTS:
                result = predict(title, description)
                Incident.objects.create(
                    reporter=citizen, title=title, description=description,
                    latitude=latitude, longitude=longitude,
                    urgency=result['urgency'], category=result['category'],
                    department=CATEGORY_TO_DEPARTMENT.get(result['category'], ''),
                    ai_reason=result['reason'], needs_review=result['needs_review'],
                )
        self.stdout.write(self.style.SUCCESS(f'Demo data ready ({created} new user(s)).'))