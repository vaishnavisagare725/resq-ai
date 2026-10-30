"""Django settings for ResQ AI.

Everything that differs between my laptop and a server comes from the environment.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')   # does not override variables that are already set


def env_list(name, default=''):
    """Read a comma-separated environment variable as a list."""
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY is missing. Add it to backend/.env (see .env.example).')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '127.0.0.1,localhost')
RENDER_HOST = os.getenv('RENDER_EXTERNAL_HOSTNAME')   # Render sets this on its servers
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts',
    'incidents',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves the admin's CSS and JS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---- Database: MySQL. A managed database needs TLS, so the CA certificate path is optional ----
DB_SSL_CA = os.getenv('DB_SSL_CA')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            **({'ssl': {'ca': DB_SSL_CA}} if DB_SSL_CA else {}),
        },
        'CONN_MAX_AGE': 60,          # reuse a connection for a minute
        'CONN_HEALTH_CHECKS': True,  # test a reused connection first, because a cloud database drops idle ones
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---- Static files (admin CSS) and uploaded photos ----
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# When CLOUDINARY_URL is set (the cloudinary package reads it itself), photos go to Cloudinary.
# Without it they go to the local media/ folder, which is what I use on my laptop.
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL', '')

STORAGES = {
    'default': {
        'BACKEND': (
            'incidents.storage.CloudinaryStorage'
            if CLOUDINARY_URL
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

# ---- REST framework ----
NUM_PROXIES = os.getenv('NUM_PROXIES')   # how many proxies sit in front of the app (leave empty if unsure)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'login': os.getenv('LOGIN_RATE', '20/min'),
        'register': os.getenv('REGISTER_RATE', '10/hour'),
    },
    'NUM_PROXIES': int(NUM_PROXIES) if NUM_PROXIES else None,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---- Who may call the API from a browser (CORS), and who may post to the admin (CSRF) ----
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
)
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

# ---- HTTPS settings: on whenever DEBUG is off (these are the warnings from check --deploy) ----
if not DEBUG:
    # the host's proxy ends TLS and tells Django which protocol the visitor used
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r'^health/$']   # the host's health check may arrive without the header
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('HSTS_SECONDS', '3600'))   # one hour first, raise it later

# Two HSTS options are decisions for the owner of the whole domain. I deploy on a shared
# platform subdomain, so I leave them off on purpose.
SILENCED_SYSTEM_CHECKS = ['security.W005', 'security.W021']

# ---- Logging: console + a rotating file (never log passwords, tokens or report text) ----
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'plain': {'format': '{asctime} {levelname} {name} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'plain'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'resq.log',
            'maxBytes': 1_000_000,
            'backupCount': 3,
            'formatter': 'plain',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'incidents': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'django.request': {'handlers': ['console', 'file'], 'level': 'WARNING', 'propagate': False},
    },
}