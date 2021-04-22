from django.contrib import admin
from django.utils.html import format_html
from code_challenge.models import CodeChallenge, CodeChallengeSubmission, UserChallengeInteraction


def latest_submission(obj):
    return format_html(f'<a href="/admin/code_challenge/codechallengesubmission/{obj.latest_submission.id}/change/">{obj}</a>')

class UserChallengeInteractionAdmin(admin.ModelAdmin):
    exclude = ('latest_submission',)
    readonly_fields = (latest_submission,)
    list_filter = ('user', 'challenge')


admin.site.register(CodeChallenge)
admin.site.register(CodeChallengeSubmission)
admin.site.register(UserChallengeInteraction, UserChallengeInteractionAdmin)
