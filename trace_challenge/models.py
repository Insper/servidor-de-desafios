from django.db import models
from core.models import ChallengeRepo, Concept
from django.conf import settings


class TraceChallenge(models.Model):
    title = models.CharField(max_length=1024)
    slug = models.SlugField()
    repo = models.ForeignKey(ChallengeRepo, on_delete=models.CASCADE)
    published = models.BooleanField(default=True)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class TraceStateSubmission(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(TraceChallenge, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    state = models.JSONField()
    state_index = models.IntegerField()
    is_last = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author.username}: {self.challenge.title}({self.creation_date}) success[{self.success}]'


class UserTraceChallengeInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(TraceChallenge, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)
    latest_state = models.IntegerField(default=-1)
    completed = models.BooleanField(default=False)
