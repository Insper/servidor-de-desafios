from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PyGymUser, Concept, ChallengeRepo


admin.site.register(PyGymUser, UserAdmin)
admin.site.register(Concept)
admin.site.register(ChallengeRepo)
