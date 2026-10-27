from .base import ApiTestCase


class FilterTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.fire = self.make(
            title='Building fire', description='Fire on the second floor',
            department='fire', category='fire', urgency='critical',
        )
        self.chest = self.make(
            title='Chest pain', description='Man at the bus stop',
            department='medical', category='medical', urgency='high', needs_review=True,
        )
        self.pothole = self.make(title='Pothole', description='Big hole on the road', urgency='low')
        self.fire.assign_responder(self.fire_boss, self.fire_boss)
        self.login(self.admin)

    def titles(self, query):
        res = self.client.get(f'/api/incidents/?{query}')
        self.assertEqual(res.status_code, 200)
        return [i['title'] for i in res.data['results']]

    def test_status(self):
        self.assertEqual(self.titles('status=assigned'), ['Building fire'])
        self.assertCountEqual(self.titles('status=open'), ['Chest pain', 'Pothole'])

    def test_urgency(self):
        self.assertEqual(self.titles('urgency=high'), ['Chest pain'])

    def test_department(self):
        self.assertEqual(self.titles('department=medical'), ['Chest pain'])

    def test_needs_review(self):
        self.assertEqual(self.titles('needs_review=true'), ['Chest pain'])

    def test_search_looks_in_title_and_description_and_ignores_case(self):
        self.assertEqual(self.titles('q=FIRE'), ['Building fire'])
        self.assertEqual(self.titles('q=road'), ['Pothole'])   # found in the description

    def test_sort_by_urgency(self):
        self.assertEqual(
            self.titles('sort=urgency'), ['Building fire', 'Chest pain', 'Pothole']
        )

    def test_active_hides_resolved_incidents(self):
        self.fire.change_status('resolved', self.fire_boss)
        self.assertCountEqual(self.titles('active=true'), ['Chest pain', 'Pothole'])
        self.assertEqual(self.titles('status=resolved'), ['Building fire'])

    def test_an_unknown_value_matches_nothing(self):
        self.assertEqual(self.titles('status=nonsense'), [])