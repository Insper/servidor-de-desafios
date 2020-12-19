from django.db import models
from core.models import ChallengeRepo, Concept


class TraceChallenge(models.Model):
    title = models.CharField(max_length=1024)
    slug = models.SlugField()
    repo = models.ForeignKey(ChallengeRepo, on_delete=models.CASCADE)
    published = models.BooleanField(default=True)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
