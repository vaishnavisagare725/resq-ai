from django.core.exceptions import ValidationError

from incidents.models import Incident

from .base import ApiTestCase


class IncidentModelTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(department='fire', category='fire')

    def test_taking_sets_status_assignee_and_history(self):
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        self.inc.refresh_from_db()
        self.assertEqual(self.inc.status, 'assigned')
        self.assertEqual(self.inc.assigned_to, self.fire_boss)
        self.assertEqual(self.inc.updates.count(), 1)

    def test_a_responder_from_another_department_is_rejected_and_nothing_changes(self):
        with self.assertRaises(ValidationError):
            self.inc.assign_responder(self.med_boss, self.med_boss)
        self.inc.refresh_from_db()
        self.assertIsNone(self.inc.assigned_to)
        self.assertEqual(self.inc.status, 'open')
        self.assertEqual(self.inc.updates.count(), 0)

    def test_a_worker_is_not_a_responder(self):
        with self.assertRaises(ValidationError):
            self.inc.assign_responder(self.fire_worker, self.fire_worker)

    def test_workers_from_another_department_are_rejected_and_nothing_changes(self):
        with self.assertRaises(ValidationError):
            self.inc.assign_workers([self.fire_worker, self.med_worker], self.fire_boss)
        self.assertEqual(self.inc.workers.count(), 0)   # not even the valid one was added
        self.assertEqual(self.inc.updates.count(), 0)

    def test_workers_need_a_department_on_the_incident(self):
        unrouted = self.make()
        with self.assertRaises(ValidationError):
            unrouted.assign_workers([self.fire_worker], self.fire_boss)

    def test_a_resolved_incident_is_locked(self):
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        self.inc.change_status('resolved', self.fire_boss)
        with self.assertRaises(ValidationError):
            self.inc.assign_workers([self.fire_worker], self.fire_boss)
        with self.assertRaises(ValidationError):
            self.inc.triage(self.fire_boss, urgency='high')

    def test_triage_records_the_change(self):
        self.inc.triage(self.fire_boss, urgency='critical', note='smoke seen')
        self.inc.refresh_from_db()
        self.assertEqual(self.inc.urgency, 'critical')
        self.assertIn('Triage by fire_boss', self.inc.updates.first().note)

    def test_triage_cannot_move_a_taken_incident_to_another_department(self):
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        with self.assertRaises(ValidationError):
            self.inc.triage(self.fire_boss, category='medical')
        self.inc.refresh_from_db()
        self.assertEqual((self.inc.category, self.inc.department), ('fire', 'fire'))

    def test_a_failed_triage_changes_nothing(self):
        with self.assertRaises(ValidationError):
            self.inc.triage(self.fire_boss, urgency='high', category='aliens')
        self.inc.refresh_from_db()
        self.assertEqual(self.inc.urgency, 'low')   # even the valid part was not applied

    def test_validators_run_on_full_clean_but_not_on_save(self):
        bad = Incident(
            reporter=self.citizen, title='x', description='long enough text here',
            latitude=200, longitude=0,
        )
        with self.assertRaises(ValidationError) as ctx:
            bad.full_clean()
        self.assertIn('latitude', ctx.exception.error_dict)
        bad.save()   # save() does NOT validate: this is why the serializer must
        self.assertTrue(Incident.objects.filter(pk=bad.pk).exists())