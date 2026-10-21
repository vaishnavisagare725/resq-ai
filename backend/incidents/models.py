import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction

from accounts.models import User

# Maps the AI's category to the department that handles it.
CATEGORY_TO_DEPARTMENT = {
    'fire': 'fire',
    'medical': 'medical',
    'flood': 'disaster',
    'accident': 'police',
}
VALID_CATEGORIES = ['fire', 'medical', 'flood', 'accident', 'other']


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
        limit_choices_to={'role': 'responder'},
    )
    workers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='field_tasks',
        limit_choices_to={'role': 'worker'},
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    category = models.CharField(max_length=30, default='other')
    department = models.CharField(max_length=20, choices=User.Department.choices, blank=True)
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.LOW)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    ai_reason = models.CharField(max_length=300, blank=True)
    needs_review = models.BooleanField(default=False)
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

    def route_department(self):
        """Pick the department from the category."""
        if not self.department:
            self.department = CATEGORY_TO_DEPARTMENT.get(self.category, '')

    def _ensure_open(self):
        if self.status == self.Status.RESOLVED:
            raise ValidationError('This incident is already resolved.')

    def triage(self, user, urgency=None, category=None, note=''):
        """A responder corrects the AI's urgency and/or category. Re-routes the department."""
        self._ensure_open()
        if urgency and urgency not in self.Urgency.values:
            raise ValidationError(f'Unknown urgency: {urgency}.')
        if category and category not in VALID_CATEGORIES:
            raise ValidationError(f'Unknown category: {category}.')

        changes = []
        new_urgency, new_category, new_department = self.urgency, self.category, self.department

        if urgency and urgency != self.urgency:
            changes.append(f'urgency {self.urgency} -> {urgency}')
            new_urgency = urgency
        if category and category != self.category:
            new_department = CATEGORY_TO_DEPARTMENT.get(category, '')
            if self.assigned_to_id and new_department != self.department:
                raise ValidationError(
                    'This incident is already taken, so its department cannot change.'
                )
            changes.append(f'category {self.category} -> {category}')
            new_category = category
        if not changes:
            raise ValidationError('Nothing to change.')

        with transaction.atomic():
            self.urgency = new_urgency
            self.category = new_category
            self.department = new_department
            self.needs_review = False
            self.save()
            text = f'Triage by {user.username}: ' + ', '.join(changes)
            IncidentUpdate.objects.create(
                incident=self,
                updated_by=user,
                old_status=self.status,
                new_status=self.status,
                note=text + (f'. {note}' if note else ''),
            )

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

    def assign_responder(self, responder, user, note=''):
        """A responder takes the case. Sets assigned_to, status and a history row."""
        self._ensure_open()
        if responder.role != 'responder':
            raise ValidationError(f'{responder.username} is not a responder.')
        if self.department and responder.department != self.department:
            raise ValidationError(
                f'{responder.username} is in {responder.department or "no"} department, '
                f'but this incident needs {self.department}.'
            )
        with transaction.atomic():
            old_status = self.status
            if not self.department:
                self.department = responder.department   # the responder claims an unrouted incident
            self.assigned_to = responder
            self.status = self.Status.ASSIGNED
            self.save()
            IncidentUpdate.objects.create(
                incident=self,
                updated_by=user,
                old_status=old_status,
                new_status=self.status,
                note=note or f'Assigned to {responder.username}',
            )

    def assign_workers(self, workers, user, note=''):
        """Add workers. They must be workers of this incident's department."""
        self._ensure_open()
        if not self.department:
            raise ValidationError('Set the incident department before adding workers.')
        for w in workers:
            if w.role != 'worker':
                raise ValidationError(f'{w.username} is not a worker.')
            if w.department != self.department:
                raise ValidationError(
                    f'{w.username} is in {w.department or "no"} department, '
                    f'but this incident needs {self.department}.'
                )
        with transaction.atomic():
            self.workers.add(*workers)
            IncidentUpdate.objects.create(
                incident=self,
                updated_by=user,
                old_status=self.status,
                new_status=self.status,
                note=note or 'Workers added: ' + ', '.join(w.username for w in workers),
            )

    def remove_workers(self, workers, user, note=''):
        """Remove workers and write a history row."""
        self._ensure_open()
        with transaction.atomic():
            self.workers.remove(*workers)
            IncidentUpdate.objects.create(
                incident=self,
                updated_by=user,
                old_status=self.status,
                new_status=self.status,
                note=note or 'Workers removed: ' + ', '.join(w.username for w in workers),
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


def incident_image_path(instance, filename):
    """Random file name grouped by incident: incidents/5/3f9a....jpg"""
    ext = os.path.splitext(filename)[1].lower()
    return f'incidents/{instance.incident_id}/{uuid.uuid4().hex}{ext}'


class IncidentImage(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='images')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_images',
    )
    image = models.ImageField(upload_to=incident_image_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Image {self.id} for incident {self.incident_id}'