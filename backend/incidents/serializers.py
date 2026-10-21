from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Incident, IncidentImage, IncidentUpdate

User = get_user_model()

MAX_IMAGE_MB = 5
MAX_IMAGES_PER_INCIDENT = 3


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'department']


class IncidentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentImage
        fields = ['id', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_image(self, value):
        if value.size > MAX_IMAGE_MB * 1024 * 1024:
            raise serializers.ValidationError(f'Image must be {MAX_IMAGE_MB} MB or smaller.')
        return value


class IncidentSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.username', read_only=True, allow_null=True
    )
    assigned_to_department = serializers.CharField(
        source='assigned_to.department', read_only=True, allow_null=True
    )
    workers = WorkerSerializer(many=True, read_only=True)
    images = IncidentImageSerializer(many=True, read_only=True)
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'latitude', 'longitude',
            'category', 'department', 'urgency', 'status',
            'reporter', 'reporter_name',
            'assigned_to', 'assigned_to_name', 'assigned_to_department',
            'workers', 'images', 'is_open', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'category', 'department', 'urgency', 'status',
            'reporter', 'assigned_to', 'created_at', 'updated_at',
        ]

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Please describe the emergency in at least 10 characters.'
            )
        return value.strip()


class WorkerIdsSerializer(serializers.Serializer):
    worker_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class NoteSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class IncidentUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source='updated_by.username', read_only=True, allow_null=True
    )

    class Meta:
        model = IncidentUpdate
        fields = ['id', 'old_status', 'new_status', 'note', 'updated_by_name', 'created_at']