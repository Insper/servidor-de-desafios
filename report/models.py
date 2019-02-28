from django.contrib.auth.models import User


class Report(User):
    class Meta:
        proxy = True
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'


class EvolutionReport(User):
    class Meta:
        proxy = True
        verbose_name = 'Evolution Report'
        verbose_name_plural = 'Evolution Reports'
