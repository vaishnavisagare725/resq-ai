import os

# the settings module refuses to load without a SECRET_KEY, so tests get a throw-away one
os.environ.setdefault('SECRET_KEY', 'test-only-secret-key-not-used-anywhere-else-0123456789')

from .settings import *  # noqa: E402,F401,F403

# MD5 is far faster than the real password hasher. NEVER use it outside tests.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# tests use plain http and a local disk for uploads, whatever the environment says
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

# silence the app's logs during tests, and stop them writing to logs/resq.log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'null': {'class': 'logging.NullHandler'}},
    'loggers': {
        'incidents': {'handlers': ['null'], 'propagate': False},
        'django.request': {'handlers': ['null'], 'propagate': False},
    },
}