"""
Django settings for pygym project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv


def create_dir(dirpath):
    try:
        dirpath.mkdir(parents=True)
    except FileExistsError:
        pass


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHALLENGES_DIR = BASE_DIR / 'raw' / 'challenge_files'
CHALLENGES_RAW_DIR = BASE_DIR / 'code_challenge' / 'static' / 'raw'
create_dir(CHALLENGES_DIR)
create_dir(CHALLENGES_RAW_DIR)
CONTENT_RAW_DIR = BASE_DIR / 'content' / 'static' / 'raw'
create_dir(CONTENT_RAW_DIR)

# Load environment variables in .env file
load_dotenv(BASE_DIR / '.env')
CORS_ALLOWED_ORIGINS = [c for c in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if c]
FRONTEND_URL = os.environ.get('FRONTEND_URL')
BACKEND_TOKEN = os.environ.get('BACKEND_TOKEN')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_SES_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SES_SECRET_ACCESS_KEY')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = 'r*gl!)m0t=x##wt##w#4t=fl6-^kk8(smd547w*oi#77=*$69a'
    print('Using development secret key. If you are in the production server you are missing the DJANGO_SECRET_KEY environment variable with the secret key.')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
USE_POSTGRES = POSTGRES_DB and POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_HOST

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PRODUCTION = False

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Application definition

INSTALLED_APPS = [
    'core',
    'frontend',
    'code_challenge',
    'trace_challenge',
    'content',
    'grade',
    'quiz',
    'thanks',
    'pygym_auth',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pygym.urls'

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

WSGI_APPLICATION = 'pygym.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {}
if USE_POSTGRES:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': '5432',
    }
else:
    print('Using sqlite3. If this is the production server you are missing the postgres environment variables.', file=sys.stderr)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

AUTH_USER_MODEL = 'core.PyGymUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = 'media/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
