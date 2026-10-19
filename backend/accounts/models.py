from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'citizen', 'Citizen'
        RESPONDER = 'responder', 'Responder'
        WORKER = 'worker', 'Worker'
        ADMIN = 'admin', 'Admin'

    class Department(models.TextChoices):
        FIRE = 'fire', 'Fire'
        MEDICAL = 'medical', 'Medical'
        POLICE = 'police', 'Police'
        DISASTER = 'disaster', 'Disaster relief'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CITIZEN)
    department = models.CharField(max_length=20, choices=Department.choices, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def clean(self):
        super().clean()
        if self.role in (self.Role.RESPONDER, self.Role.WORKER) and not self.department:
            raise ValidationError({'department': 'Department is required for responders and workers.'})

    def __str__(self):
        return f'{self.username} ({self.role})'