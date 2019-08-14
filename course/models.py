from django.db import models
from django.contrib.auth.models import User
from challenges.models import Challenge
from datetime import timedelta, datetime


class Class(models.Model):
    name = models.CharField(max_length=1024, blank=True)
    students = models.ManyToManyField(User)
    start_date = models.DateField('date started', blank=True, null=True)
    end_date = models.DateField('date ended', blank=True, null=True)

    def __str__(self):
        return self.name


class ChallengeBlock(models.Model):
    name = models.CharField(max_length=1024, blank=True)
    release_date = models.DateTimeField('release date', blank=True, null=True)
    block_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    challenges = models.ManyToManyField(Challenge)

    def __str__(self):
        return self.name


class DateRange:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def __iter__(self):
        if self.start_date is None or self.end_date is None:
            return []
        for n in range(int((self.end_date - self.start_date).days)+1):
            yield self.start_date + timedelta(n)


def get_daterange(user):
    user_classes = Class.objects.filter(students__id=user.id)
    today = datetime.now().date()
    start = None
    for c in user_classes.all():
        if c.start_date and c.end_date and c.start_date <= today and today <= c.end_date:
            if start is None or c.start_date < start:
                start = c.start_date
    return DateRange(start, today)
