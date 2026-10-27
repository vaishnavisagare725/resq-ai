from django.contrib.admin.sites import AdminSite

from incidents.admin import IncidentUpdateInline
from incidents.models import Incident

from .base import ApiTestCase
from .test_admin import form_data


class HistoryEndpointTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(department='fire', category='fire')
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        self.inc.assign_workers([self.fire_worker], self.fire_boss)
        self.inc.change_status('resolved', self.fire_worker, 'Fire put out')
        self.url = f'/api/incidents/{self.inc.id}/updates/'

    def test_the_reporter_reads_the_whole_timeline(self):
        self.login(self.citizen)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 3)
        self.assertEqual(
            {row['note'] for row in res.data},
            {'Assigned to fire_boss', 'Workers added: fire_w', 'Fire put out'},
        )
        self.assertEqual(
            set(res.data[0]),
            {'id', 'old_status', 'new_status', 'note', 'updated_by_name', 'created_at'},
        )

    def test_the_timeline_is_newest_first(self):
        self.login(self.citizen)
        dates = [row['created_at'] for row in self.client.get(self.url).data]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_it_records_who_did_each_step(self):
        self.login(self.citizen)
        by_note = {row['note']: row['updated_by_name'] for row in self.client.get(self.url).data}
        self.assertEqual(by_note['Fire put out'], 'fire_w')
        self.assertEqual(by_note['Assigned to fire_boss'], 'fire_boss')

    def test_people_who_may_see_the_incident_can_read_it(self):
        for user in (self.fire_boss, self.fire_worker, self.admin):
            with self.subTest(user.username):
                self.login(user)
                self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_strangers_get_404_and_anonymous_gets_401(self):
        for user in (self.citizen2, self.med_boss, self.med_worker):
            with self.subTest(user.username):
                self.login(user)
                self.assertEqual(self.client.get(self.url).status_code, 404)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url).status_code, 401)


class AdminLayersTests(ApiTestCase):
    def test_a_worker_is_rejected_by_the_field_before_clean_runs(self):
        inc = self.make(department='fire', category='fire')
        from incidents.admin import IncidentAdminForm

        form = IncidentAdminForm(
            data=form_data(inc, assigned_to=self.fire_worker.id), instance=inc
        )
        self.assertFalse(form.is_valid())
        # limit_choices_to is the first layer, so this is the field's message, not clean()'s
        self.assertIn('valid choice', ' '.join(form.errors['assigned_to']))

    def test_the_history_inline_is_read_only(self):
        inline = IncidentUpdateInline(Incident, AdminSite())
        self.assertFalse(inline.has_add_permission(request=None))