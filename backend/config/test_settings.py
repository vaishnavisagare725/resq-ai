from .settings import *  # noqa: F401,F403

# MD5 is far faster than the real password hasher. NEVER use it outside tests.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

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