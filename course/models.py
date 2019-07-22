from django.db import models
from django.contrib.auth.models import User
from challenges.models import Challenge


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
