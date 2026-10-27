from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserNameTests(TestCase):
    def test_str_shows_the_username_and_role(self):
        user = User.objects.create_user(
            'ravi', password='Sturdy-Pass-2026!', role='worker', department='fire'
        )
        self.assertEqual(str(user), 'ravi (worker)')