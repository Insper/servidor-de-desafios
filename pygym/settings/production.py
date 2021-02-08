from .base import *
import requests


DEBUG = False
PRODUCTION = True

PUBLIC_IPv4 = requests.get('https://api.ipify.org').text
ALLOWED_HOSTS = [PUBLIC_IPv4, 'softdes.insper.edu.br']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_ROOT = "/var/www/softdes/static"
MEDIA_ROOT = "/var/www/softdes/media"

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[DJANGO] %(levelname)s %(asctime)s %(module)s '
                          '%(name)s.%(funcName)s:%(lineno)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            }
        },
        'loggers': {
            '*': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            }
        },
    }
