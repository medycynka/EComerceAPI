"""
Django settings for ECommerceAPI project.

Generated by 'django-admin startproject' using Django 3.2.18.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=w2h1b2^-*@wmits30aje@jmn!jpd&j7-)4j1b@n+@x3=8sk63'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ##
    'rest_framework',
    'django_filters',
    ##
    'graphene_django',
    ##
    'django_countries',
    ##
    'crispy_forms',
    'crispy_bootstrap5',
    ##
    'debug_toolbar',
    ##
    'API.apps.ApiConfig',
    'GraphQL.apps.GraphqlConfig',
    'UserInterface.apps.UserinterfaceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'ECommerceAPI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ECommerceAPI.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# DRF
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Graphene
GRAPHENE = {
    "SCHEMA": "GraphQL.schema.schema",
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
    ],
}

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Debug Toolbar
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

# Django countries
COUNTRIES_FLAG_URL = "assets/flags/{code}.gif"

# Custom project variables
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_EMAIL_ADDRESS = os.environ.get('DEFAULT_EMAIL_ADDRESS', 'shop.example@platform.com')

THUMBNAIL_SIZE = (200, 300)

PAYMENT_DEADLINE_DAYS = int(os.environ.get('PAYMENT_DEADLINE_DAYS', 5))

USER_CLIENT_GROUP_NAME = 'Client'
USER_SELLER_GROUP_NAME = 'Seller'
USERS_CUSTOM_GROUPS = (
    USER_CLIENT_GROUP_NAME,
    USER_SELLER_GROUP_NAME
)
DEFAULT_USER_CUSTOM_GROUP = USER_CLIENT_GROUP_NAME

# Data upload
# 2MB - 2097152
# 4MB - 4194304
# 8MB - 8388608
# 16MB - 16777216
# 32MB - 33554432
# 64MB - 67108684
DATA_UPLOAD_MAX_MEMORY_SIZE = 8388608   # 8MB

DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S.%f",
    "%d/%m/%Y %H:%M",
    "%d/%m/%y %H:%M:%S",
    "%d/%m/%y %H:%M:%S.%f",
    "%d/%m/%y %H:%M",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M:%S.%f",
    "%d.%m.%Y %H:%M",
    "%d.%m.%y %H:%M:%S",
    "%d.%m.%y %H:%M:%S.%f",
    "%d.%m.%y %H:%M",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S.%f",
    "%d-%m-%Y %H:%M",
    "%d-%m-%y %H:%M:%S",
    "%d-%m-%y %H:%M:%S.%f",
    "%d-%m-%y %H:%M",
]

USE_ASYNC_TASK_COLLECTOR = int(os.environ.get("USE_ASYNC_TASK_COLLECTOR", 0))
TASK_COLLECTOR_REFRESH_RATE = int(os.environ.get("TASK_COLLECTOR_REFRESH_RATE", 60 * 60 * 24))   # every 24 hours

# include local_settings
try:
    from .local_settings import *
except ModuleNotFoundError as mnfe:
    pass
except ImportError as ie:
    pass
except Exception as e:
    pass
