from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction


class Incident(models.Model):
    class Urgency(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        ASSIGNED = 'assigned', 'Assigned'
        RESOLVED = 'resolved', 'Resolved'

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    category = models.CharField(max_length=30, default='other')
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.LOW)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'urgency']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.title} ({self.urgency})'

    @property
    def is_open(self):
        return self.status != self.Status.RESOLVED

    def change_status(self, new_status, user, note=''):
        """Change the status and write a history row. All or nothing."""
        with transaction.atomic():
            old_status = self.status
            self.status = new_status
            self.save()
            IncidentUpdate.objects.create(
                incident=self,
                updated_by=user,
                old_status=old_status,
                new_status=new_status,
                note=note,
            )


class IncidentUpdate(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incident_updates',
    )
    old_status = models.CharField(max_length=10, choices=Incident.Status.choices)
    new_status = models.CharField(max_length=10, choices=Incident.Status.choices)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.incident_id}: {self.old_status} -> {self.new_status}'