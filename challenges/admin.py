from django.contrib import admin

from .models import TesteDeMesa, Challenge, ChallengeSubmission, Prova
from django.contrib.admin.filters import RelatedFieldListFilter


class FilterComboBox(RelatedFieldListFilter):
    template = 'filter_template.html'


class ChallengeSubmissionAdmin(admin.ModelAdmin):
    list_filter = [('author', FilterComboBox), ('challenge', FilterComboBox)]
    list_display = ('author', 'challenge')

    def soft_delete(self, request, queryset):
        queryset.update(deleted=True)
    soft_delete.short_description = 'Soft delete selecionados'

    actions = ['soft_delete']


admin.site.register(TesteDeMesa)
admin.site.register(Challenge)
admin.site.register(ChallengeSubmission, ChallengeSubmissionAdmin)
admin.site.register(Prova)
