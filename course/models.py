from django.db import models
from django.contrib.auth.models import User


class Class(models.Model):
    name = models.CharField(max_length=1024, blank=True)

    students = models.ManyToManyField(User)

    def __str__(self):
        return self.name
