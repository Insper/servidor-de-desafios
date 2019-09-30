import os
from django.conf import settings
from django.utils import timezone


LOG_DIR = os.path.join(settings.BASE_DIR, 'logs/')
DATE_FORMAT = '%Y-%m-%d'


class LogIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = timezone.now()
        for fname in os.listdir(LOG_DIR):
            filename = os.path.join(LOG_DIR, fname)
            log_date_str = '-'.join(fname.split('-')[-3:]).replace('.txt', '')
            log_date = timezone.datetime.strptime(log_date_str, DATE_FORMAT).date()
            time_delta = now.date() - log_date
            if time_delta.days > 7:
                os.remove(filename)
        filename = os.path.join(LOG_DIR, 'ip-log-{0}.txt'.format(now.strftime(DATE_FORMAT)))
        ip = self.visitor_ip_address(request)
        with open(filename, 'a') as logfile:
            logfile.write('{0},{1},{2}\n'.format(now, request.user.username, ip))
        response = self.get_response(request)
        return response

    def visitor_ip_address(self, request):
        '''Source: https://www.science-emergence.com/Articles/How-to-get-visitor-ip-address-with-django-/'''
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
