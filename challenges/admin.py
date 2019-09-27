from django.contrib import admin

from .models import Challenge, ChallengeSubmission, Prova

admin.site.register(Challenge)
admin.site.register(ChallengeSubmission)
admin.site.register(Prova)