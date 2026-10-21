from django import forms
from django.contrib import admin

from .models import Incident, IncidentImage, IncidentUpdate


class IncidentAdminForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        dept = cleaned.get('department')
        assigned = cleaned.get('assigned_to')
        workers = cleaned.get('workers')

        if assigned:
            if assigned.role != 'responder':
                self.add_error(
                    'assigned_to',
                    'Assigned to must be a responder. Put field workers in the Workers box.',
                )
            else:
                if not dept:                       # the responder claims an unrouted incident
                    dept = assigned.department
                    cleaned['department'] = dept
                if assigned.department != dept:
                    self.add_error(
                        'assigned_to',
                        f'{assigned.username} is in {assigned.department or "no"} department, '
                        f'but this incident needs {dept}.',
                    )
                elif cleaned.get('status') == 'open':
                    cleaned['status'] = 'assigned'  # a responder took the case

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


class IncidentImageInline(admin.TabularInline):
    model = IncidentImage
    extra = 0
    readonly_fields = ('uploaded_by', 'created_at')


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    form = IncidentAdminForm
    list_display = ('title', 'urgency', 'status', 'category', 'department',
                    'reporter', 'assigned_to', 'created_at')
    list_filter = ('urgency', 'status', 'category', 'department')
    search_fields = ('title', 'description')
    list_select_related = ('reporter', 'assigned_to')
    inlines = [IncidentUpdateInline, IncidentImageInline]
    actions = ['mark_resolved']
    filter_horizontal = ('workers',)

    def save_model(self, request, obj, form, change):
        old_status = Incident.objects.get(pk=obj.pk).status if change else None
        super().save_model(request, obj, form, change)
        if change and old_status != obj.status:
            IncidentUpdate.objects.create(
                incident=obj,
                updated_by=request.user,
                old_status=old_status,
                new_status=obj.status,
                note='Edited in admin',
            )

    @admin.action(description='Mark selected incidents as resolved')
    def mark_resolved(self, request, queryset):
        count = 0
        for incident in queryset.exclude(status='resolved'):
            incident.change_status('resolved', request.user, 'Resolved from admin')
            count += 1
        self.message_user(request, f'{count} incident(s) marked as resolved.')