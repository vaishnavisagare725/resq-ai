import threading

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from incidents.models import Incident

User = get_user_model()


class TakeRaceTests(TransactionTestCase):
    def test_only_one_responder_wins(self):
        make = User.objects.create_user
        citizen = make('c', password='Sturdy-Pass-2026!')
        fire = make('r1', password='Sturdy-Pass-2026!', role='responder', department='fire')
        medical = make('r2', password='Sturdy-Pass-2026!', role='responder', department='medical')
        incident = Incident.objects.create(
            reporter=citizen, title='Need help',
            description='Please send someone to the market', latitude=18.5, longitude=73.8,
        )   # unrouted, so BOTH responders may take it

        codes = []
        start_together = threading.Barrier(2)

        def attempt(user):
            try:
                client = APIClient()
                client.force_authenticate(user)
                start_together.wait()
                codes.append(client.post(f'/api/incidents/{incident.id}/take/').status_code)
            finally:
                connection.close()   # each thread has its own database connection

        threads = [threading.Thread(target=attempt, args=(u,)) for u in (fire, medical)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(sorted(codes), [200, 400])
        self.assertEqual(incident.updates.count(), 1)   # one winner, one history row