from django.contrib import admin
from coding_challenge.models import ChallengeRepo, CodingChallenge, CodingChallengeSubmission


admin.site.register(ChallengeRepo)
admin.site.register(CodingChallenge)
admin.site.register(CodingChallengeSubmission)
