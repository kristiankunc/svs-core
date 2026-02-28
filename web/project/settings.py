import os

from pathlib import Path

from dotenv import load_dotenv

from svs_core.shared.env_manager import EnvManager

EnvManager.load_env_file()

from svs_core.db.settings import DATABASES as SVS_DATABASES

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    exit("Error: DJANGO_SECRET_KEY not set")

DEBUG = os.getenv("DJANGO_DEBUG", False).lower() in ("true", "1", "t")


ALLOWED_HOSTS = (
    os.getenv("DJANGO_ALLOWED_HOSTS", "localhost, 127.0.0.1")
    .replace(" ", "")
    .split(",")
)

CSRF_TRUSTED_ORIGINS = (
    os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "https://localhost, https://127.0.0.1")
    .replace(" ", "")
    .split(",")
)

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "svs_core.apps.SvsCoreConfig",
    "app",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "app" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "app.lib.user_injector.user_render_injector",
                "django.template.context_processors.debug",
            ],
        },
    },
]

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

WSGI_APPLICATION = "project.wsgi.application"

DATABASES = SVS_DATABASES

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-sessions",
    }
}

INTERNAL_IPS = ("127.0.0.1",)

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security Settings
# HTTPS/SSL settings - only enabled in production (DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS with 1-year duration is standard for production
    # Ensure HTTPS is working correctly before deploying to production
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Security headers - enabled regardless of DEBUG mode
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# Security Audit Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "security_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "security.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "security": {
            "handlers": ["security_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
