from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import IncidentViewSet, WorkerListView

router = DefaultRouter()
router.register('incidents', IncidentViewSet, basename='incident')

urlpatterns = router.urls + [
    path('workers/', WorkerListView.as_view()),
]