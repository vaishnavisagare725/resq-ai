from django import forms
from django.contrib import admin

from .models import Incident, IncidentUpdate


class IncidentAdminForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        dept = cleaned.get('department')
        workers = cleaned.get('workers')
        if workers:
            if not dept:
                raise forms.ValidationError('Set the incident department before adding workers.')
            wrong = [w.username for w in workers if w.department != dept]
            if wrong:
                self.add_error(
                    'workers',
                    f'Wrong department: {", ".join(wrong)}. This incident needs {dept} workers.',
                )
        return cleaned


class IncidentUpdateInline(admin.TabularInline):
    model = IncidentUpdate
    extra = 0
    can_delete = False
    readonly_fields = ('old_status', 'new_status', 'updated_by', 'note', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    form = IncidentAdminForm
    list_display = ('title', 'urgency', 'status', 'category', 'department',
                    'reporter', 'assigned_to', 'created_at')
    list_filter = ('urgency', 'status', 'category', 'department')
    search_fields = ('title', 'description')
    list_select_related = ('reporter', 'assigned_to')
    inlines = [IncidentUpdateInline]
    actions = ['mark_resolved']
    filter_horizontal = ('workers',)

    @admin.action(description='Mark selected incidents as resolved')
    def mark_resolved(self, request, queryset):
        count = 0
        for incident in queryset.exclude(status='resolved'):
            incident.change_status('resolved', request.user, 'Resolved from admin')
            count += 1
        self.message_user(request, f'{count} incident(s) marked as resolved.')