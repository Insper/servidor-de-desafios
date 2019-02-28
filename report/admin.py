from django.contrib import admin
from django.contrib.auth.models import User
from .models import Report, EvolutionReport, TutorialsReport
from challenges.models import Challenge, ChallengeSubmission
from tutorials.models import Tutorial, TutorialAccess


class CustomAdmin(admin.ModelAdmin):
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
            return False, response

        return True, response


@admin.register(Report)
class ReportAdmin(CustomAdmin):
    change_list_template = 'admin/report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
            return response

        users = User.objects.filter(is_staff=False).exclude(username='aluno.teste')

        response.context_data['users'] = users
        response.context_data['submissions'] = {user: {s.challenge: s for s in ChallengeSubmission.submissions_by_challenge(user)} for user in users}
        response.context_data['challenges'] = Challenge.objects.all()

        return response


@admin.register(EvolutionReport)
class EvolutionReportAdmin(CustomAdmin):
    change_list_template = 'admin/evolution_report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
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


@admin.register(TutorialsReport)
class TutorialsReportAdmin(CustomAdmin):
    change_list_template = 'admin/tutorials_report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
            return response

        users = User.objects.filter(is_staff=False).exclude(username='aluno.teste')
        tutorials = Tutorial.all_published()
        accesses = TutorialAccess.objects.filter(user__in=users, tutorial__in=tutorials)
        accesses_by_user = {}
        for access in accesses:
            if access.user not in accesses_by_user:
                accesses_by_user[access.user] = {}
            accesses_by_user[access.user][access.tutorial] = access.access_count
        for user in users:
            if user not in accesses_by_user:
                accesses_by_user[user] = {}
            for tutorial in tutorials:
                if tutorial not in accesses_by_user[user]:
                    accesses_by_user[user][tutorial] = 0

        response.context_data['users'] = users
        response.context_data['tutorials'] = tutorials
        response.context_data['accesses_by_user'] = accesses_by_user

        return response