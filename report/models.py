from django.db import models
from django.contrib.auth.models import User


class Report(User):
    class Meta:
        proxy = True
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
