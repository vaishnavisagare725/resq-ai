from django.contrib.auth import get_user_model

from incidents.models import Incident

from .base import PASSWORD, ApiTestCase

User = get_user_model()


class VisibilityTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.mine = self.make(self.citizen, title='mine')
        self.other = self.make(self.citizen2, title='other')
        self.fire = self.make(self.citizen2, title='fire', department='fire', category='fire')
        self.med = self.make(self.citizen2, title='med', department='medical', category='medical')
        self.fire.workers.add(self.fire_worker)

    def titles(self, user):
        self.login(user)
        res = self.client.get('/api/incidents/')
        self.assertEqual(res.status_code, 200)
        return {i['title'] for i in res.data['results']}

    def test_each_role_sees_only_what_it_should(self):
        self.assertEqual(self.titles(self.citizen), {'mine'})
        self.assertEqual(self.titles(self.citizen2), {'other', 'fire', 'med'})
        self.assertEqual(self.titles(self.fire_worker), {'fire'})
        self.assertEqual(self.titles(self.fire_boss), {'mine', 'other', 'fire'})   # own department + unrouted
        self.assertEqual(self.titles(self.med_boss), {'mine', 'other', 'med'})
        self.assertEqual(self.titles(self.admin), {'mine', 'other', 'fire', 'med'})

    def test_anonymous_gets_401(self):
        self.assertEqual(self.client.get('/api/incidents/').status_code, 401)

    def test_a_hidden_incident_is_404_not_403(self):
        self.login(self.citizen)
        self.assertEqual(self.client.get(f'/api/incidents/{self.other.id}/').status_code, 404)
        self.login(self.fire_boss)
        self.assertEqual(self.client.get(f'/api/incidents/{self.med.id}/').status_code, 404)

    def test_the_owner_can_open_the_detail(self):
        self.login(self.citizen)
        self.assertEqual(self.client.get(f'/api/incidents/{self.mine.id}/').status_code, 200)


class CreateTests(ApiTestCase):
    FIRE = {
        'title': 'Building fire',
        'description': 'Fire on second floor, people trapped',
        'latitude': 18.5,
        'longitude': 73.8,
    }

    def post(self, **change):
        return self.client.post('/api/incidents/', {**self.FIRE, **change}, format='json')

    def test_the_ai_fills_the_fields_and_i_am_the_reporter(self):
        self.login(self.citizen)
        res = self.post()
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['urgency'], 'critical')
        self.assertEqual(res.data['category'], 'fire')
        self.assertEqual(res.data['department'], 'fire')
        self.assertEqual(res.data['reporter_name'], 'cit1')

    def test_the_client_cannot_fake_ai_fields_or_the_reporter(self):
        self.login(self.citizen)
        res = self.post(
            title='Help', description='Please help me quickly',
            urgency='critical', category='fire', department='fire',
            status='resolved', reporter=self.citizen2.id,
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['urgency'], 'low')
        self.assertEqual(res.data['category'], 'other')
        self.assertEqual(res.data['department'], '')
        self.assertEqual(res.data['status'], 'open')
        self.assertEqual(res.data['reporter_name'], 'cit1')

    def test_bad_input_is_rejected(self):
        self.login(self.citizen)
        bad = [
            ('latitude 200', {'latitude': 200}),
            ('longitude -181', {'longitude': -181}),
            ('short description', {'description': 'fire'}),
            ('blank title', {'title': ''}),
            ('text latitude', {'latitude': 'north'}),
        ]
        for label, change in bad:
            with self.subTest(label):
                self.assertEqual(self.post(**change).status_code, 400)
        self.assertEqual(Incident.objects.count(), 0)

    def test_anonymous_cannot_create(self):
        self.assertEqual(self.post().status_code, 401)

    def test_an_unclear_report_waits_for_review(self):
        self.login(self.citizen)
        res = self.post(title='Pothole', description='There is a big pothole on the main road')
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data['needs_review'])
        self.assertEqual(res.data['department'], '')


class TakeTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(department='fire', category='fire', urgency='critical')
        self.url = f'/api/incidents/{self.inc.id}/take/'

    def test_a_citizen_a_worker_and_an_admin_cannot_take(self):
        for user in (self.citizen, self.fire_worker, self.admin):
            with self.subTest(user.username):
                self.login(user)
                self.assertEqual(self.client.post(self.url).status_code, 403)

    def test_the_right_responder_takes_it(self):
        self.login(self.fire_boss)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['status'], 'assigned')
        self.assertEqual(res.data['assigned_to_name'], 'fire_boss')
        self.assertEqual(self.inc.updates.count(), 1)

    def test_it_cannot_be_taken_twice(self):
        self.login(self.fire_boss)
        self.client.post(self.url)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)
        self.assertIn('already taken', res.data['detail'])

    def test_another_department_cannot_even_see_it(self):
        self.login(self.med_boss)
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_taking_an_unrouted_incident_sets_its_department(self):
        unrouted = self.make()
        self.login(self.med_boss)
        res = self.client.post(f'/api/incidents/{unrouted.id}/take/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['department'], 'medical')


class WorkerTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(department='fire', category='fire')
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        self.add = f'/api/incidents/{self.inc.id}/add-workers/'
        self.remove = f'/api/incidents/{self.inc.id}/remove-workers/'

    def add_ids(self, user, ids):
        self.login(user)
        return self.client.post(self.add, {'worker_ids': ids}, format='json')

    def test_the_owner_adds_a_worker_of_the_same_department(self):
        res = self.add_ids(self.fire_boss, [self.fire_worker.id])
        self.assertEqual(res.status_code, 200)
        self.assertEqual([w['username'] for w in res.data['workers']], ['fire_w'])
        self.assertIn('Workers added: fire_w', self.inc.updates.first().note)

    def test_a_worker_of_another_department_is_rejected(self):
        res = self.add_ids(self.fire_boss, [self.med_worker.id])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(self.inc.workers.count(), 0)

    def test_bad_ids_are_rejected(self):
        self.assertEqual(self.add_ids(self.fire_boss, [self.citizen.id]).status_code, 400)  # not a worker
        self.assertEqual(self.add_ids(self.fire_boss, [999999]).status_code, 400)           # does not exist
        self.assertEqual(self.add_ids(self.fire_boss, []).status_code, 400)                 # empty list

    def test_a_worker_cannot_add_workers(self):
        self.assertEqual(self.add_ids(self.fire_worker, [self.fire_worker.id]).status_code, 403)

    def test_a_second_responder_of_the_same_department_cannot_manage_it(self):
        other = User.objects.create_user(
            'fire_boss2', password=PASSWORD, role='responder', department='fire'
        )
        # can see it (same department), but it is not theirs: object-level permission
        self.assertEqual(self.add_ids(other, [self.fire_worker.id]).status_code, 403)

    def test_an_admin_can_manage_it(self):
        self.assertEqual(self.add_ids(self.admin, [self.fire_worker.id]).status_code, 200)

    def test_remove_a_worker(self):
        self.add_ids(self.fire_boss, [self.fire_worker.id])
        res = self.client.post(self.remove, {'worker_ids': [self.fire_worker.id]}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.inc.workers.count(), 0)

    def test_removing_someone_who_is_not_on_it_is_rejected(self):
        self.login(self.fire_boss)
        res = self.client.post(self.remove, {'worker_ids': [self.fire_worker.id]}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_nothing_changes_after_it_is_resolved(self):
        self.inc.change_status('resolved', self.fire_boss)
        self.assertEqual(self.add_ids(self.fire_boss, [self.fire_worker.id]).status_code, 400)


class ResolveTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.inc = self.make(department='fire', category='fire')
        self.inc.assign_responder(self.fire_boss, self.fire_boss)
        self.inc.assign_workers([self.fire_worker], self.fire_boss)
        self.url = f'/api/incidents/{self.inc.id}/resolve/'

    def test_a_worker_on_the_incident_resolves_it_and_is_recorded(self):
        self.login(self.fire_worker)
        res = self.client.post(self.url, {'note': 'Fire put out'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['status'], 'resolved')
        last = self.inc.updates.first()
        self.assertEqual(last.updated_by, self.fire_worker)
        self.assertEqual(last.note, 'Fire put out')

    def test_the_owning_responder_can_resolve(self):
        self.login(self.fire_boss)
        self.assertEqual(self.client.post(self.url).status_code, 200)

    def test_a_worker_who_is_not_on_it_cannot_even_see_it(self):
        other = User.objects.create_user(
            'fire_w2', password=PASSWORD, role='worker', department='fire'
        )
        self.login(other)
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_the_reporter_cannot_resolve(self):
        self.login(self.citizen)
        self.assertEqual(self.client.post(self.url).status_code, 403)

    def test_it_cannot_be_resolved_twice(self):
        self.login(self.fire_boss)
        self.client.post(self.url)
        self.assertEqual(self.client.post(self.url).status_code, 400)

    def test_an_untaken_incident_cannot_be_resolved(self):
        untaken = self.make(department='fire', category='fire')
        self.login(self.admin)
        res = self.client.post(f'/api/incidents/{untaken.id}/resolve/')
        self.assertEqual(res.status_code, 400)


class TriageTests(ApiTestCase):
    def triage(self, inc, body):
        return self.client.post(f'/api/incidents/{inc.id}/triage/', body, format='json')

    def test_a_responder_corrects_the_urgency_and_it_is_recorded(self):
        inc = self.make(department='fire', category='fire', needs_review=True)
        self.login(self.fire_boss)
        res = self.triage(inc, {'urgency': 'critical', 'note': 'smoke seen'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['urgency'], 'critical')
        self.assertFalse(res.data['needs_review'])
        self.assertTrue(inc.updates.first().note.startswith('Triage by fire_boss'))

    def test_triage_can_re_route_an_unrouted_incident(self):
        inc = self.make()
        self.login(self.fire_boss)
        res = self.triage(inc, {'category': 'medical'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['department'], 'medical')
        # now it belongs to the medical team: invisible to fire, visible to medical
        self.assertEqual(self.client.get(f'/api/incidents/{inc.id}/').status_code, 404)
        self.login(self.med_boss)
        self.assertEqual(self.client.get(f'/api/incidents/{inc.id}/').status_code, 200)

    def test_the_department_of_a_taken_incident_cannot_change(self):
        inc = self.make(department='fire', category='fire')
        inc.assign_responder(self.fire_boss, self.fire_boss)
        self.login(self.fire_boss)
        self.assertEqual(self.triage(inc, {'category': 'medical'}).status_code, 400)
        inc.refresh_from_db()
        self.assertEqual(inc.category, 'fire')

    def test_bad_requests_are_rejected(self):
        inc = self.make()
        self.login(self.fire_boss)
        for body in ({}, {'urgency': 'urgent'}, {'category': 'aliens'}, {'urgency': 'low'}):
            with self.subTest(body=body):
                self.assertEqual(self.triage(inc, body).status_code, 400)

    def test_a_citizen_cannot_triage(self):
        inc = self.make()
        self.login(self.citizen)
        self.assertEqual(self.triage(inc, {'urgency': 'high'}).status_code, 403)

    def test_only_the_owner_can_triage_a_taken_incident(self):
        inc = self.make(department='fire', category='fire')
        inc.assign_responder(self.fire_boss, self.fire_boss)
        other = User.objects.create_user(
            'fire_boss2', password=PASSWORD, role='responder', department='fire'
        )
        self.login(other)
        self.assertEqual(self.triage(inc, {'urgency': 'high'}).status_code, 403)


class SummaryAndMapTests(ApiTestCase):
    def test_cards_map_and_list_agree_for_every_role(self):
        a = self.make(self.citizen, department='fire', category='fire', urgency='critical')
        a.assign_responder(self.fire_boss, self.fire_boss)
        a.assign_workers([self.fire_worker], self.fire_boss)
        self.make(self.citizen2, department='medical', category='medical', urgency='high')
        self.make(self.citizen2)   # unrouted
        done = self.make(self.citizen, department='fire', category='fire')
        done.assign_responder(self.fire_boss, self.fire_boss)
        done.change_status('resolved', self.fire_boss)

        everyone = (self.citizen, self.citizen2, self.fire_boss, self.med_boss,
                    self.fire_worker, self.admin)
        for user in everyone:
            with self.subTest(user.username):
                self.login(user)
                s = self.client.get('/api/incidents/summary/').data
                m = self.client.get('/api/incidents/map/').data
                active = self.client.get('/api/incidents/?active=true').data['count']
                self.assertEqual(len(m['results']), s['open'] + s['assigned'])
                self.assertEqual(active, s['open'] + s['assigned'])
                self.assertTrue(all(p['status'] != 'resolved' for p in m['results']))
                self.assertFalse(m['truncated'])

    def test_the_map_needs_a_token(self):
        self.assertEqual(self.client.get('/api/incidents/map/').status_code, 401)

    def test_the_map_lists_the_most_urgent_first(self):
        self.make(urgency='low')
        self.make(urgency='critical')
        self.make(urgency='high')
        self.login(self.admin)
        urgencies = [p['urgency'] for p in self.client.get('/api/incidents/map/').data['results']]
        self.assertEqual(urgencies, ['critical', 'high', 'low'])


class WorkerListTests(ApiTestCase):
    def test_a_responder_sees_only_their_department(self):
        self.login(self.fire_boss)
        res = self.client.get('/api/workers/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual([w['username'] for w in res.data], ['fire_w'])

    def test_an_admin_can_filter_by_department(self):
        self.login(self.admin)
        res = self.client.get('/api/workers/?department=medical')
        self.assertEqual([w['username'] for w in res.data], ['med_w'])

    def test_citizens_and_workers_are_refused(self):
        for user in (self.citizen, self.fire_worker):
            with self.subTest(user.username):
                self.login(user)
                self.assertEqual(self.client.get('/api/workers/').status_code, 403)