from django.contrib import admin

from .models import Challenge, ChallengeSubmission, Prova
from django.contrib.admin.filters import RelatedFieldListFilter

class FilterComboBox(RelatedFieldListFilter):
    template = 'filter_template.html'

class ChallengeSubmissionAdmin(admin.ModelAdmin):
    list_filter = [('author', FilterComboBox), ('challenge', FilterComboBox)]
    list_display = ('author', 'challenge')

admin.site.register(Challenge)
admin.site.register(ChallengeSubmission, ChallengeSubmissionAdmin)
admin.site.register(Prova)