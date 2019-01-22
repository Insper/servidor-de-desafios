from django.contrib import admin

from .models import Challenge, ChallengeSubmission

admin.site.register(Challenge)
admin.site.register(ChallengeSubmission)