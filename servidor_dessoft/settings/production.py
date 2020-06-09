from .base import *
import requests

DEBUG = False
DEV_SERVER = False

PUBLIC_IPv4 = requests.get('https://api.ipify.org').text #For local dev, use: "localhost"
ALLOWED_HOSTS = [PUBLIC_IPv4, 'softdes.insper.edu.br'] #For local dev, use: ["localhost", "127.0.0.1"]

STATIC_ROOT = "/var/www/softdes/static"
MEDIA_ROOT = "/var/www/softdes/media"