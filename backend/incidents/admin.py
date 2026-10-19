from django.contrib import admin

from .models import Incident, IncidentUpdate


class IncidentUpdateInline(admin.TabularInline):
    model = IncidentUpdate
    extra = 0
    can_delete = False
    readonly_fields = ('old_status', 'new_status', 'updated_by', 'note', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'urgency', 'status', 'category', 'reporter', 'assigned_to', 'created_at')
    list_filter = ('urgency', 'status', 'category')
    search_fields = ('title', 'description')
    list_select_related = ('reporter', 'assigned_to')
    inlines = [IncidentUpdateInline]
    actions = ['mark_resolved']

    @admin.action(description='Mark selected incidents as resolved')
    def mark_resolved(self, request, queryset):
        for incident in queryset:
            incident.change_status('resolved', request.user, 'Resolved from admin')
        self.message_user(request, f'{queryset.count()} incident(s) marked as resolved.')