from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class UserTag(models.Model):
    tag = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)

    def __str__(self):
        return self.tag


class PyGymUser(AbstractUser):
    additional_quiz_time_percent = models.FloatField(default=0)
    additional_quiz_time_absolute = models.IntegerField(default=0)
    tags = models.ManyToManyField(UserTag, related_name='users')


class EmailToken(models.Model):
    user = models.ForeignKey(PyGymUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=16)
    creation_date = models.DateTimeField(auto_now_add=True)


class Semester(models.Model):
    year = models.IntegerField()
    semester = models.IntegerField()

    def __str__(self):
        return f'{self.year}-{self.semester}'


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


class ChallengeRepo(models.Model):
    remote = models.CharField(max_length=1024)
    slug = models.SlugField()
    last_commit = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.slug} ({self.remote})'
