from .base import *
import requests

DEBUG = False
DEV_SERVER = False

PUBLIC_IPv4 = requests.get('https://api.ipify.org').text
ALLOWED_HOSTS = [PUBLIC_IPv4, 'softdes.insper.edu.br']
STATIC_ROOT = '/home/ubuntu/softdes/staticfiles'
