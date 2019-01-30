from django.contrib import admin

from .models import Tutorial, TutorialAccess

admin.site.register(Tutorial)
admin.site.register(TutorialAccess)