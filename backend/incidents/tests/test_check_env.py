import os
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

GOOD = {
    'SECRET_KEY': 'x',
    'DB_NAME': 'defaultdb',
    'DB_USER': 'avnadmin',
    'DB_PASSWORD': 'secret-value',
    'DB_HOST': 'db.example.com',
    'DB_PORT': '3306',
}


def run(**env):
    out = StringIO()
    with mock.patch.dict(os.environ, env, clear=True):
        call_command('check_env', stdout=out)
    return out.getvalue()


@override_settings(DEBUG=False)
class CheckEnvTests(SimpleTestCase):
    def test_a_complete_environment_passes_and_warns_about_the_optional_ones(self):
        text = run(**GOOD)
        self.assertIn('not set: CLOUDINARY_URL', text)
        self.assertIn('Environment looks fine', text)

    def test_missing_names_are_listed_but_values_are_never_printed(self):
        env = {key: value for key, value in GOOD.items() if key != 'DB_HOST'}
        with self.assertRaises(CommandError) as ctx:
            run(**env)
        self.assertIn('DB_HOST', str(ctx.exception))
        self.assertNotIn('secret-value', str(ctx.exception))

    def test_a_database_on_localhost_is_refused_in_production(self):
        with self.assertRaises(CommandError) as ctx:
            run(**{**GOOD, 'DB_HOST': 'localhost'})
        self.assertIn('localhost', str(ctx.exception))