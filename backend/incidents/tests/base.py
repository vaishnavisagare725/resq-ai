import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

from incidents.models import Incident

User = get_user_model()
PASSWORD = 'Sturdy-Pass-2026!'


class ApiTestCase(APITestCase):
    """Shared users and helpers for the API tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.disable(logging.CRITICAL)   # keep the test output clean

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        make = User.objects.create_user
        cls.citizen = make('cit1', password=PASSWORD)
        cls.citizen2 = make('cit2', password=PASSWORD)
        cls.fire_boss = make('fire_boss', password=PASSWORD, role='responder', department='fire')
        cls.med_boss = make('med_boss', password=PASSWORD, role='responder', department='medical')
        cls.fire_worker = make('fire_w', password=PASSWORD, role='worker', department='fire')
        cls.med_worker = make('med_w', password=PASSWORD, role='worker', department='medical')
        cls.admin = make('boss', password=PASSWORD, role='admin')

    def setUp(self):
        cache.clear()   # throttle counters live in the cache

    def login(self, user):
        self.client.force_authenticate(user)   # skip the password and token, the role is what we test

    def make(self, reporter=None, **fields):
        data = {
            'title': 'Test incident',
            'description': 'Something is happening here right now',
            'latitude': 18.5,
            'longitude': 73.8,
        }
        data.update(fields)
        return Incident.objects.create(reporter=reporter or self.citizen, **data)