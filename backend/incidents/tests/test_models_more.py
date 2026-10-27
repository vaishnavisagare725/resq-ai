from django.core.exceptions import ValidationError

from incidents.models import IncidentImage

from .base import ApiTestCase


class ModelExtrasTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(
            title='Building fire', department='fire', category='fire', urgency='critical'
        )

    def test_readable_names(self):
        self.assertEqual(str(self.inc), 'Building fire (critical)')
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        self.assertEqual(str(self.inc.updates.first()), f'{self.inc.id}: open -> assigned')
        self.assertIn('for incident', str(IncidentImage(incident=self.inc)))

    def test_is_open_follows_the_status(self):
        self.assertTrue(self.inc.is_open)
        self.inc.status = 'resolved'
        self.assertFalse(self.inc.is_open)

    def test_route_department_uses_the_category_and_respects_a_choice_already_made(self):
        flood = self.make(category='flood')
        flood.route_department()
        self.assertEqual(flood.department, 'disaster')

        chosen = self.make(category='medical', department='fire')
        chosen.route_department()
        self.assertEqual(chosen.department, 'fire')          # not overwritten

        other = self.make(category='other')
        other.route_department()
        self.assertEqual(other.department, '')               # nothing to route to

    def test_triage_rejects_unknown_values(self):
        with self.assertRaises(ValidationError):
            self.inc.triage(self.fire_boss, urgency='urgent')
        with self.assertRaises(ValidationError):
            self.inc.triage(self.fire_boss, category='aliens')

    def test_a_non_worker_cannot_be_added_as_a_worker(self):
        with self.assertRaises(ValidationError):
            self.inc.assign_workers([self.citizen], self.fire_boss)

    def test_removing_workers_is_recorded(self):
        self.inc.assign_workers([self.fire_worker], self.fire_boss)
        self.inc.remove_workers([self.fire_worker], self.fire_boss)
        self.assertEqual(self.inc.workers.count(), 0)
        self.assertEqual(self.inc.updates.first().note, 'Workers removed: fire_w')