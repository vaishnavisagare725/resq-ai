from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from rest_framework.test import APITestCase
from rest_framework.throttling import ScopedRateThrottle

User = get_user_model()
STRONG = 'Sturdy-Pass-2026!'


class AuthApiTests(APITestCase):
    def setUp(self):
        cache.clear()   # throttle counters live in the cache

    def register(self, **extra):
        data = {'username': 'ravi', 'email': 'ravi@example.com', 'password': STRONG, **extra}
        return self.client.post('/api/auth/register/', data, format='json')

    def login(self, username='ravi', password=STRONG):
        return self.client.post(
            '/api/auth/login/', {'username': username, 'password': password}, format='json'
        )

    def test_register_creates_a_citizen_and_hides_the_password(self):
        res = self.register()
        self.assertEqual(res.status_code, 201)
        self.assertNotIn('password', res.data)
        user = User.objects.get(username='ravi')
        self.assertEqual(user.role, 'citizen')
        self.assertTrue(user.check_password(STRONG))          # stored as a hash, not text
        self.assertNotEqual(user.password, STRONG)

    def test_register_ignores_role_and_department(self):
        res = self.register(role='admin', department='fire', is_staff=True, is_superuser=True)
        self.assertEqual(res.status_code, 201)
        user = User.objects.get(username='ravi')
        self.assertEqual((user.role, user.department), ('citizen', ''))
        self.assertFalse(user.is_staff or user.is_superuser)

    def test_register_rejects_weak_passwords_and_duplicates(self):
        self.assertEqual(self.register(password='12345678').status_code, 400)
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.register().status_code, 400)    # same username again

    def test_login_returns_tokens_and_the_user(self):
        User.objects.create_user('ravi', password=STRONG)
        res = self.login()
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.data['user']['username'], 'ravi')

    def test_wrong_password_is_401(self):
        User.objects.create_user('ravi', password=STRONG)
        self.assertEqual(self.login(password='wrong').status_code, 401)

    def test_me_needs_a_token_and_works_with_one(self):
        User.objects.create_user('ravi', password=STRONG)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
        access = self.login().data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['username'], 'ravi')

    def test_a_tampered_token_is_refused(self):
        User.objects.create_user('ravi', password=STRONG)
        access = self.login().data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access[:-3]}abc')
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)

    def test_the_refresh_token_gives_a_new_access_token(self):
        User.objects.create_user('ravi', password=STRONG)
        refresh = self.login().data['refresh']
        res = self.client.post('/api/auth/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)

    def test_repeated_logins_are_throttled(self):
        User.objects.create_user('ravi', password=STRONG)
        rates = {'login': '3/min', 'register': '10/hour'}
        with mock.patch.object(ScopedRateThrottle, 'THROTTLE_RATES', rates):
            codes = [self.login(password='wrong').status_code for _ in range(5)]
        self.assertEqual(codes, [401, 401, 401, 429, 429])


class UserModelTests(SimpleTestCase):
    def test_a_responder_or_worker_needs_a_department(self):
        for role in ('responder', 'worker'):
            with self.subTest(role):
                with self.assertRaises(ValidationError) as ctx:
                    User(username='x', role=role).clean()
                self.assertIn('department', ctx.exception.message_dict)

    def test_a_citizen_does_not(self):
        User(username='y', role='citizen').clean()   # no error