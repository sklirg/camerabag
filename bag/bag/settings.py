"""
Django settings for bag project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('CB_SECRET_KEY', '(8_6qiej*ga!ux=@^c29%^w(88w%zh2=8qfk%_d@so64!#pu+u')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('CB_DJANGO_DEBUG', '').lower() == 'true'

ALLOWED_HOSTS = '*' if DEBUG else os.getenv('CB_ALLOWED_HOSTS', 'camerabag.sklirg.io').replace(' ', '').split(',')


# Application definition

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + [
    # Third party apps
    'graphene_django',
    'corsheaders',
] + [
    # Own apps
    'apps.gallery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bag.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'bag.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Oslo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

S3_BUCKET = os.getenv('CB_S3_BUCKET', '')
USE_S3 = S3_BUCKET != ''
S3_BUCKET_ID = '' if not USE_S3 else \
    (S3_BUCKET[:-1].split('/')[-1] if S3_BUCKET[-1] == '/' else S3_BUCKET.split('/')[-1])

S3_AWS_ACCESS_KEY = os.getenv('CB_S3_AWS_ACCESS_KEY', None)
S3_AWS_SECRET_KEY = os.getenv('CB_S3_AWS_SECRET_KEY', None)

MEDIA_URL = S3_BUCKET if USE_S3 else '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_URL = os.getenv("CB_CELERY_BROKER", "redis://localhost:6379")
CELERY_TASK_ALWAYS_EAGER = os.getenv("CB_CELERY_EAGER", f"{DEBUG}") == "True"
CELERY_TIMEZONE = TIME_ZONE

GRAPHENE = {
    'RELAY_CONNECTION_MAX_LIMIT': 2500
}
