from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Q, When
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Incident
from .permissions import (
    CanAddImages,
    IsAssignedResponderOrAdmin,
    IsOnIncidentOrAdmin,
    IsResponder,
)
from .serializers import (
    MAX_IMAGES_PER_INCIDENT,
    IncidentImageSerializer,
    IncidentSerializer,
    IncidentUpdateSerializer,
    NoteSerializer,
    WorkerIdsSerializer,
)

User = get_user_model()

URGENCY_RANK = Case(
    When(urgency='critical', then=0),
    When(urgency='high', then=1),
    When(urgency='medium', then=2),
    default=3,
    output_field=IntegerField(),
)


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    http_method_names = ['get', 'post', 'head', 'options']   # changes go through the actions below

    def get_permissions(self):
        if self.action == 'take':
            return [IsResponder()]
        if self.action in ('add_workers', 'remove_workers'):
            return [IsAssignedResponderOrAdmin()]
        if self.action == 'resolve':
            return [IsOnIncidentOrAdmin()]
        if self.action == 'images':
            return [CanAddImages()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Incident.objects
            .select_related('reporter', 'assigned_to')
            .prefetch_related('workers', 'images')
        )

        # who may see which rows
        if user.role == 'citizen':
            qs = qs.filter(reporter=user)
        elif user.role == 'worker':
            qs = qs.filter(workers=user)
        elif user.role == 'responder':
            qs = qs.filter(Q(department=user.department) | Q(department=''))
        # admin: sees everything

        # optional filters from the URL
        params = self.request.query_params
        for field in ('status', 'urgency', 'department'):
            value = params.get(field)
            if value:
                qs = qs.filter(**{field: value})
        text = params.get('q')
        if text:
            qs = qs.filter(Q(title__icontains=text) | Q(description__icontains=text))
        if params.get('sort') == 'urgency':
            qs = qs.annotate(rank=URGENCY_RANK).order_by('rank', '-created_at')
        return qs

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def _fresh(self, incident):
        """Reload the incident so the response shows the new workers, images and status."""
        fresh = (
            Incident.objects
            .select_related('reporter', 'assigned_to')
            .prefetch_related('workers', 'images')
            .get(pk=incident.pk)
        )
        return self.get_serializer(fresh).data

    # POST /api/incidents/<id>/take/
    @action(detail=True, methods=['post'])
    def take(self, request, pk=None):
        incident = self.get_object()
        if incident.assigned_to_id:
            return Response({'detail': 'This incident is already taken.'}, status=400)
        incident.assign_responder(request.user, request.user)
        return Response(self._fresh(incident))

    # POST /api/incidents/<id>/add-workers/   {"worker_ids": [4, 5]}
    @action(detail=True, methods=['post'], url_path='add-workers')
    def add_workers(self, request, pk=None):
        incident = self.get_object()
        s = WorkerIdsSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        ids = set(s.validated_data['worker_ids'])
        workers = list(User.objects.filter(id__in=ids, role='worker'))
        if len(workers) != len(ids):
            return Response({'detail': 'Some ids are not workers.'}, status=400)
        incident.assign_workers(workers, request.user)
        return Response(self._fresh(incident))

    # POST /api/incidents/<id>/remove-workers/   {"worker_ids": [4]}
    @action(detail=True, methods=['post'], url_path='remove-workers')
    def remove_workers(self, request, pk=None):
        incident = self.get_object()
        s = WorkerIdsSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        workers = list(incident.workers.filter(id__in=s.validated_data['worker_ids']))
        if not workers:
            return Response({'detail': 'None of these workers are on this incident.'}, status=400)
        incident.remove_workers(workers, request.user)
        return Response(self._fresh(incident))

    # POST /api/incidents/<id>/resolve/   {"note": "Fire put out"}
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        incident = self.get_object()
        if incident.status != Incident.Status.ASSIGNED:
            return Response({'detail': 'Only an assigned incident can be resolved.'}, status=400)
        s = NoteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        incident.change_status(
            Incident.Status.RESOLVED, request.user, s.validated_data.get('note', '')
        )
        return Response(self._fresh(incident))

    # GET /api/incidents/<id>/updates/
    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        incident = self.get_object()
        rows = incident.updates.select_related('updated_by')
        return Response(IncidentUpdateSerializer(rows, many=True).data)

    # POST /api/incidents/<id>/images/   (multipart form, field name: image)
    @action(detail=True, methods=['post'])
    def images(self, request, pk=None):
        incident = self.get_object()
        if incident.status == Incident.Status.RESOLVED:
            return Response({'detail': 'This incident is already resolved.'}, status=400)
        if incident.images.count() >= MAX_IMAGES_PER_INCIDENT:
            return Response(
                {'detail': f'At most {MAX_IMAGES_PER_INCIDENT} images per incident.'}, status=400
            )
        s = IncidentImageSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save(incident=incident, uploaded_by=request.user)
        return Response(self._fresh(incident), status=201)