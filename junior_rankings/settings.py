import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = not os.environ.get("PRODUCTION")
SECRET_KEY = os.environ.get("SECRET_KEY", "this-secret-is-bad")
ALLOWED_HOSTS = [
    "localhost",
    "junior-rankings.archerygb.org",
    "archerygb-junior-rankings-4a3f3b147588.herokuapp.com",
]


# Application definition

INSTALLED_APPS = [
    "junior_rankings",
    "webpack_loader",
    "django_object_actions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "junior_rankings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "junior_rankings.wsgi.application"


# Database
DATABASES = {
    "default": dj_database_url.config(default="postgres://localhost/junior_rankings"),
    # "agb": dj_database_url.config(env="AGB_DATABASE_URL", default="postgres://localhost/agb_junior_rankings"),
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Password validation
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


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "build")]
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "build", "webpack-stats.json"),
    },
}

AGB_API_TOKEN = os.environ.get("AGB_API_TOKEN", "")
