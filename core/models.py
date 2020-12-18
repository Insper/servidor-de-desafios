from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings


class PyGymUser(AbstractUser):
    pass


class Concept(models.Model):
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    order = models.IntegerField(default=99)

    class Meta:
        ordering = ['order', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class UserConceptInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)
    total_challenges = models.IntegerField(default=0)
    successful_challenges = models.IntegerField(default=0)
