from django.contrib import admin
from code_challenge.models import CodeChallenge, CodeChallengeSubmission, UserChallengeInteraction


admin.site.register(CodeChallenge)
admin.site.register(CodeChallengeSubmission)
admin.site.register(UserChallengeInteraction)
