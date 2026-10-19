from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Incident
from .serializers import IncidentSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']   # PATCH/DELETE arrive on Day 7

    def get_queryset(self):
        user = self.request.user
        qs = (
            Incident.objects
            .select_related('reporter', 'assigned_to')
            .prefetch_related('workers')
        )

        if user.role == 'citizen':
            qs = qs.filter(reporter=user)
        elif user.role == 'worker':
            qs = qs.filter(workers=user)
        elif user.role == 'responder':
            qs = qs.filter(Q(department=user.department) | Q(department=''))
        # admin: sees everything

        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        urgency = self.request.query_params.get('urgency')
        if urgency:
            qs = qs.filter(urgency=urgency)
        return qs

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)