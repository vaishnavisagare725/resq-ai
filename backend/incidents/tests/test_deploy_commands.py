import os
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from incidents.models import Incident

User = get_user_model()


def run(name, **env):
    out = StringIO()
    with mock.patch.dict(os.environ, env):
        call_command(name, stdout=out)
    return out.getvalue()


class EnsureAdminTests(TestCase):
    ENV = {'ADMIN_USERNAME': 'siteadmin', 'ADMIN_PASSWORD': 'Sturdy-Pass-2026!'}

    def test_it_creates_the_admin_once(self):
        run('ensure_admin', **self.ENV)
        admin = User.objects.get(username='siteadmin')
        self.assertEqual((admin.role, admin.is_superuser), ('admin', True))
        self.assertTrue(admin.check_password('Sturdy-Pass-2026!'))
        self.assertIn('already exists', run('ensure_admin', **self.ENV))
        self.assertEqual(User.objects.filter(username='siteadmin').count(), 1)

    def test_it_does_nothing_without_settings(self):
        message = run('ensure_admin', ADMIN_USERNAME='', ADMIN_PASSWORD='')
        self.assertIn('no admin created', message)
        self.assertEqual(User.objects.count(), 0)


class SeedDemoTests(TestCase):
    ENV = {'DEMO_PASSWORD': 'Demo-Pass-2026!'}

    def test_it_creates_the_accounts_and_reports(self):
        run('seed_demo', **self.ENV)
        self.assertEqual(User.objects.count(), 5)
        responder = User.objects.get(username='demo_fire_responder')
        self.assertEqual((responder.role, responder.department), ('responder', 'fire'))
        self.assertTrue(responder.check_password('Demo-Pass-2026!'))
        fire = Incident.objects.get(title='Building fire')
        self.assertEqual((fire.urgency, fire.category, fire.department), ('critical', 'fire', 'fire'))
        self.assertEqual(Incident.objects.count(), 4)

    def test_running_it_twice_changes_nothing(self):
        run('seed_demo', **self.ENV)
        self.assertIn('0 new user(s)', run('seed_demo', **self.ENV))
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(Incident.objects.count(), 4)

    def test_it_does_nothing_without_a_password(self):
        message = run('seed_demo', DEMO_PASSWORD='')
        self.assertIn('no demo data created', message)
        self.assertEqual(User.objects.count(), 0)