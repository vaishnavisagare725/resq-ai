from types import SimpleNamespace
from unittest import mock

from django.contrib.admin.sites import AdminSite

from incidents.admin import IncidentAdmin, IncidentAdminForm
from incidents.models import Incident

from .base import ApiTestCase


def form_data(incident, **change):
    """What the admin form would submit for this incident."""
    data = {
        'reporter': incident.reporter_id,
        'assigned_to': incident.assigned_to_id or '',
        'workers': [w.id for w in incident.workers.all()],
        'title': incident.title,
        'description': incident.description,
        'latitude': incident.latitude,
        'longitude': incident.longitude,
        'category': incident.category,
        'department': incident.department,
        'urgency': incident.urgency,
        'status': incident.status,
        'ai_reason': incident.ai_reason,
        'needs_review': incident.needs_review,
    }
    data.update(change)
    return data


class AdminFormTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(department='fire', category='fire')

    def form(self, incident=None, **change):
        incident = incident or self.inc
        return IncidentAdminForm(data=form_data(incident, **change), instance=incident)

    def test_a_valid_form_passes(self):
        self.assertTrue(self.form().is_valid())

    def test_a_worker_cannot_be_the_responder(self):
        form = self.form(assigned_to=self.fire_worker.id)
        self.assertFalse(form.is_valid())
        self.assertIn('assigned_to', form.errors)

    def test_a_responder_from_another_department_is_refused(self):
        form = self.form(assigned_to=self.med_boss.id)
        self.assertFalse(form.is_valid())
        self.assertIn('needs fire', ' '.join(form.errors['assigned_to']))

    def test_assigning_the_right_responder_marks_the_incident_assigned(self):
        form = self.form(assigned_to=self.fire_boss.id)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['status'], 'assigned')

    def test_a_responder_claims_the_department_of_an_unrouted_incident(self):
        unrouted = self.make()
        form = self.form(unrouted, assigned_to=self.fire_boss.id)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['department'], 'fire')

    def test_workers_must_belong_to_the_incident_department(self):
        form = self.form(workers=[self.med_worker.id])
        self.assertFalse(form.is_valid())
        self.assertIn('Wrong department', ' '.join(form.errors['workers']))

    def test_workers_need_a_department_first(self):
        unrouted = self.make()
        form = self.form(unrouted, workers=[self.fire_worker.id])
        self.assertFalse(form.is_valid())
        self.assertIn('department', ' '.join(form.non_field_errors()))


class AdminActionTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.model_admin = IncidentAdmin(Incident, AdminSite())
        self.request = SimpleNamespace(user=self.admin)

    def test_changing_the_status_in_the_admin_is_recorded(self):
        inc = self.make()
        inc.status = 'assigned'
        self.model_admin.save_model(self.request, inc, form=None, change=True)
        row = inc.updates.get()
        self.assertEqual((row.old_status, row.new_status), ('open', 'assigned'))
        self.assertEqual(row.updated_by, self.admin)
        self.assertEqual(row.note, 'Edited in admin')

    def test_editing_without_changing_the_status_leaves_no_history(self):
        inc = self.make()
        inc.title = 'A new title'
        self.model_admin.save_model(self.request, inc, form=None, change=True)
        self.assertEqual(inc.updates.count(), 0)

    def test_creating_in_the_admin_leaves_no_history(self):
        inc = Incident(
            reporter=self.citizen, title='x', description='long enough text here',
            latitude=1, longitude=1,
        )
        self.model_admin.save_model(self.request, inc, form=None, change=False)
        self.assertEqual(inc.updates.count(), 0)

    def test_the_resolve_action_skips_resolved_incidents(self):
        a = self.make(department='fire', category='fire')
        a.assign_responder(self.fire_boss, self.fire_boss)
        b = self.make(department='fire', category='fire')
        b.assign_responder(self.fire_boss, self.fire_boss)
        b.change_status('resolved', self.fire_boss)
        history_before = b.updates.count()

        with mock.patch.object(self.model_admin, 'message_user') as message:
            self.model_admin.mark_resolved(
                self.request, Incident.objects.filter(pk__in=[a.pk, b.pk])
            )

        a.refresh_from_db()
        self.assertEqual(a.status, 'resolved')
        self.assertEqual(b.updates.count(), history_before)        # no useless "resolved -> resolved" row
        self.assertIn('1 incident(s)', message.call_args.args[1])