from django.db import models
from challenges.models import *
from django.contrib.auth.models import User


class UserChallengeReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    best_result = models.CharField(max_length=5, choices=[(res, res.value) for res in Result], blank=True)

    class Meta:
        unique_together = ('user', 'challenge',)

    @classmethod
    def submissions_by_user(cls, users):
        user_challenges = {u.id: {} for u in users}
        for challenge_report in cls.objects.all():
            if challenge_report.user_id in user_challenges:
                user_challenges[challenge_report.user_id][challenge_report.challenge_id] = challenge_report
        return user_challenges
