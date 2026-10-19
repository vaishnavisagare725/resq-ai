from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Incident

User = get_user_model()


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'department']


class IncidentSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.username', read_only=True, allow_null=True
    )
    assigned_to_department = serializers.CharField(
        source='assigned_to.department', read_only=True, allow_null=True
    )
    workers = WorkerSerializer(many=True, read_only=True)
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'latitude', 'longitude',
            'category', 'department', 'urgency', 'status',
            'reporter', 'reporter_name',
            'assigned_to', 'assigned_to_name', 'assigned_to_department',
            'workers', 'is_open', 'created_at', 'updated_at',
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