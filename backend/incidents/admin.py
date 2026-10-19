from django.contrib import admin
from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'urgency', 'status', 'category', 'reporter', 'assigned_to', 'created_at')
    list_filter = ('urgency', 'status', 'category')
    search_fields = ('title', 'description')