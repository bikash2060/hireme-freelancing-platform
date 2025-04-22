from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

# Define base directory path for the project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key for Django project; keep it confidential in production.
SECRET_KEY = "django-insecure-y9vjmoy_i9&x-5!dq7w-dq+fsts@dsmut9(yp)$)lyg%rd43_x"

# Debug mode setting; should be False in production.
DEBUG = True

# List of allowed hostnames for the application.
ALLOWED_HOSTS = ['*']

SITE_ID = 1

# Installed apps for the project, including Django and custom apps
INSTALLED_APPS = [
    # Django built-in apps
    "django.contrib.admin",
    'django.contrib.sites',
    'django.contrib.auth',
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    "channels",

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    
    # Custom apps
    "accounts",
    "chat",
    "clientprofile",
    "dashboard",
    "freelancerprofile",
    "home",
    "notification",
    "projects",
    "proposals",
]

# Middleware stack for request/response processing
MIDDLEWARE = [
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "accounts.middleware.UserActivityMiddleware",
]

# Message storage backend for the project
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Root URL configuration for the project
ROOT_URLCONF = "freelancing_app.urls"

# Templates configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / 'templates',
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "notification.context_processors.notifications",
            ],
        },
    },
]

# WSGI application entry point for the project
WSGI_APPLICATION = "freelancing_app.wsgi.application"

ASGI_APPLICATION = "freelancing_app.asgi.application"

# Channel layers configuration for WebSocket support
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Database configuration for MySQL backend
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hireme_db',
        'USER': 'root',
        'PASSWORD': 'Bishal@123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'accounts.utils.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Login and redirect URLs
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_LOGIN_ON_GET = True

# Use our custom social account adapter
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = False

# Basic allauth settings
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"

# Google OAuth provider settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'VERIFIED_EMAIL': True,
    }
}

# Language and timezone settings
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('ne', _('Nepali')),
]

TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_L10N = True
USE_TZ = False

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files settings
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'bishalbhattarai472@gmail.com'
EMAIL_HOST_PASSWORD = 'auqv lisg jxjh sjis'

# Contact details
COMPANY_NAME = 'HireMe Nepal Pvt. Ltd.'
LOCATION = 'Baneshwor, Kathmandu, Nepal'
CONTACT_EMAIL = 'bishalbhattarai472@gmail.com'
SUPPORT_EMAIL = 'support@hiremeapp.com'
CONTACT_PHONE = '+977 9860000000'
CONTACT_PHONE_2 = '+977 9860000001'
ADMIN_EMAIL = 'bishalbhattarai472@gmail.com'


# Reserved usernames that users can't register with
RESERVED_USERNAMES = {
    "admin", "administrator", "root", "superuser", "sysadmin", 
    "moderator", "support", "helpdesk", "service", "client",
    "freelancer", "user", "guest", "owner", "manager",
    "staff", "team", "developer", "dev", "test",
    "system", "operator", "security", "bot", "official"
}