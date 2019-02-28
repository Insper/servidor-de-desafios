from django.contrib import admin
from django.contrib.auth.models import User
from .models import Report, EvolutionReport
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


@admin.register(EvolutionReport)
class EvolutionReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/evolution_report_change_list.html'

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

        has_attempt = {user: sum(1 if len(s.submissions) > 0 else 0 for s in ChallengeSubmission.submissions_by_challenge(user)) for user in users}
        gave_up = {user: sum(1 if len(s.submissions) > 0 and s.best_result != 'OK' else 0 for s in ChallengeSubmission.submissions_by_challenge(user)) for user in users}
        ratio = {user: '-' if has_attempt[user] == 0 else '{0:.2f}%'.format(100 * gave_up[user] / has_attempt[user]) for user in users}
        response.context_data['users'] = users
        response.context_data['has_attempt'] = has_attempt
        response.context_data['gave_up'] = gave_up
        response.context_data['ratio'] = ratio

        return response