import os
import sys
from pathlib import Path

import graypy
from django.contrib.messages import constants as messages
from loguru import logger

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

GRAYLOG_PORT = 12201
GRAYLOG_SERVER_IP = "localhost"

logger.remove()


# handler = GelfUdpHandler(host=GRAYLOG_SERVER_IP, port=GRAYLOG_PORT)

# handler = graypy.GELFUDPHandler(GRAYLOG_SERVER_IP, GRAYLOG_PORT)
# logging.getLogger().addHandler(handler)


filter_dict = {
    "": "WARNING",
    "django": "INFO",
    "general_ledger.management.utils": "TRACE",
    "general_ledger": "INFO",
    "general_ledger.helpers": "DEBUG",
    "general_ledger.helpers.book": "INFO",
    "general_ledger.helpers.invoice": "DEBUG",
}


logger.add(
    "log/loguru.log",
    colorize=True,
    level="TRACE",
    format="<yellow>{time:HH:mm:ss}</yellow> "
    "<level>{level: <5}</level> |{module}|{name}|"
    "<cyan>{file.name}</cyan>:<cyan>{line}</cyan> <level>{message}</level>",
)

logger.add(
    sys.stderr,
    colorize=True,
    level="TRACE",
    filter=filter_dict,
    format="<red>{time:HH:mm:ss}</red> "
    "<level>{level: <5}</level> |"
    "<cyan>{file.name}</cyan>:<cyan>{line}</cyan> <level>{message}</level>",
)

# logger.add(handler, serialize=True)
# logger.add(
#     handler,
#     level="INFO",
#     serialize=True,
#     # filter=map_level_to_gelf,
# )
# logger.level("FATAL", no=60, color="<red>", icon="!!!")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-nqpfp)*_d#e#@lkmj1an(6tt4u%7cm!#aotod=@fcqhu&5d@#t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        # "handlers": ["file", "console"],
        "handlers": ["file", "richconsole"],
        "level": "DEBUG",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["sql"],
            "level": "DEBUG",
            "propagate": False,
        },
        "general_ledger": {
            "handlers": ["general_ledger"],
            "level": "WARNING",
        },
        "general_ledger.models.book": {
            "handlers": ["general_ledger"],
            "level": "WARNING",
            "propagate": False,
        },
        "factory.generate": {
            "handlers": ["file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "faker.factory": {
            "handlers": ["file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "TransactionModel": {
            "handlers": ["general_ledger"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            # "formatter": "sql",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "richconsole": {
            "class": "rich.logging.RichHandler",
            # "formatter": "verbose",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "log/general.log",
            "formatter": "verbose",
            "level": "INFO",
        },
        "debug": {
            "class": "logging.FileHandler",
            "filename": "log/debug.log",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "django": {
            "class": "logging.FileHandler",
            "filename": "log/django.log",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "django.template": {
            "class": "logging.FileHandler",
            "filename": "log/django.template.log",
            "formatter": "verbose",
            "level": "INFO",
        },
        "sql": {
            "class": "logging.FileHandler",
            "filename": "log/sql.log",
            "formatter": "sql",
            "level": "DEBUG",
        },
        "psycopg.pq": {
            "class": "logging.FileHandler",
            "filename": "log/psycopg.pq.log",
            "formatter": "verbose",
            "level": "INFO",
        },
        "general_ledger": {
            "class": "logging.FileHandler",
            "filename": "log/general_ledger.log",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "sql": {
            "()": "general_ledger.sql_formatter.SQLFormatter",
            "format": "[%(duration).3f] %(statement)s",
        },
    },
}

# Application definition

INSTALLED_APPS = [
    "simple_history",
    "general_ledger",
    "jazzmin",
    "django_browser_reload",
    "debug_toolbar",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django_jinja.contrib._humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_select2",
    "django_filters",
    "dynamic_preferences",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "formset",
    # "notifications",
    "import_export",
    "dashboard",
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "general_ledger.middleware.ActiveBookMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "dashboard.urls"

TEMPLATES = [
    {
        "BACKEND": "django_jinja.jinja2.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".j2",
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "dynamic_preferences.processors.global_preferences",
            ],
            "globals": {
                "render_form": "formset.templatetags.formsetify.render_form",
            },
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "general_ledger" / "templates", BASE_DIR / "templates"],
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

WSGI_APPLICATION = "dashboard.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(os.getenv("DJANGO_WORKDIR", BASE_DIR / "workdir")) / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "general_ledger" / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "BROWSABLE_API_RENDER_STYLE": {
        "default": True,
        "css": {
            "all": ("css/rest-api.css",),
        },
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Some Fancy API",
    "DESCRIPTION": "General Ledger API made with Django Rest Framework",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # OTHER SETTINGS
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_EXCEPTION_REPORTER = (
    "general_ledger.utils.exception_reporter.MyExceptionReporter"
)
