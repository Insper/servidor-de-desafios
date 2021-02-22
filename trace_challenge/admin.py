from django.contrib import admin
from trace_challenge.models import TraceChallenge, TraceStateSubmission, UserTraceChallengeInteraction


admin.site.register(TraceChallenge)
admin.site.register(TraceStateSubmission)
admin.site.register(UserTraceChallengeInteraction)
