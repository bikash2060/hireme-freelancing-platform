from pathlib import Path

# Define base directory path for the project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key for Django project; keep it confidential in production.
SECRET_KEY = "django-insecure-y9vjmoy_i9&x-5!dq7w-dq+fsts@dsmut9(yp)$)lyg%rd43_x"

# Debug mode setting; should be False in production.
DEBUG = True

# List of allowed hostnames for the application.
ALLOWED_HOSTS = []

# Installed apps for the project, including Django and custom apps.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "home",
    "accounts",
    "clientdashboard",
    "profiles",
]

# Middleware stack for request/response processing.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Define message storage backend for the project.
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Root URL configuration for the project.
ROOT_URLCONF = "freelancing_app.urls"


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
            ],
        },
    },
]

# WSGI application entry point for the project.
WSGI_APPLICATION = "freelancing_app.wsgi.application"

# Database configuration for MySQL backend.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fyp_database',
        'USER': 'root',
        'PASSWORD': 'Bishal@123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Validators for enforcing strong user passwords.
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

# Language and timezone settings for the application.
LANGUAGE_CODE = "en-us"

# Timezone setting for Nepal.
TIME_ZONE = 'Asia/Kathmandu'

# Enable internationalization support.
USE_I18N = True

# Disable timezone-aware datetimes.
USE_TZ = False

# Static file URL and directories for CSS, JavaScript, and images.
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",  
]

# Default type for auto-incrementing primary key fields.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuration for sending emails using Gmail's SMTP server.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "bishalbhattarai472@gmail.com"
EMAIL_HOST_PASSWORD = "cdjeylhnykmsmjbm"