from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class DateRange:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def __iter__(self):
        if self.start_date is None or self.end_date is None:
            return []
        for n in range(int((self.end_date - self.start_date).days) + 1):
            yield self.start_date + timedelta(n)


def tz_agora():
    return timezone.now()


def inc_dia():
    return relativedelta(days=1)


def dec_dia():
    return relativedelta(days=-1)


def tz_delta(*args, **kwargs):
    return tz_agora() + relativedelta(*args, **kwargs)


def tz_amanha():
    return tz_delta(days=1)


def tz_ontem():
    return tz_delta(days=-1)
