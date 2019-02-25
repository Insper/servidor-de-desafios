from django.contrib import admin
from django.contrib.auth.models import User
from .models import Report
from challenges.models import Challenge, ChallengeSubmission


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/report_change_list.html'

    class Media:
        css = {
            'all': ('css/report/report.css',)
        }

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        users = User.objects.filter(is_staff=False).exclude(username='aluno.teste')

        response.context_data['users'] = users
        response.context_data['submissions'] = {user: {s.challenge: s for s in ChallengeSubmission.submissions_by_challenge(user)} for user in users}
        response.context_data['challenges'] = Challenge.objects.all()

        return response