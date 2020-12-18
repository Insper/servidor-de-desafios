from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PyGymUser, Concept


admin.site.register(PyGymUser, UserAdmin)
admin.site.register(Concept)
