from .base import *
import requests


DEBUG = False
PRODUCTION = True

PUBLIC_IPv4 = requests.get('https://api.ipify.org').text
ALLOWED_HOSTS = [PUBLIC_IPv4, 'softdes.insper.edu.br']
STATIC_ROOT = '/home/ubuntu/pygym/staticfiles'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
