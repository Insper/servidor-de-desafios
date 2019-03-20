from datetime import timedelta, datetime
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from .models import *
from challenges.models import Challenge, ChallengeSubmission
from tutorials.models import Tutorial, TutorialAccess
from course.models import Class


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


class ClassFilter(SimpleListFilter):
    title = 'Class'
    parameter_name = 'class'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Class.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(class__id__exact=self.value())
        return queryset.order_by('username')


class CustomAdmin(admin.ModelAdmin):
    list_filter = (ClassFilter,)

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

    def get_queryset(self, request):
        qs = super(CustomAdmin, self).get_queryset(request)
        return qs.filter(is_staff=False).exclude(username='aluno.teste')


@admin.register(Report)
class ReportAdmin(CustomAdmin):
    change_list_template = 'admin/report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
            return response

        users = response.context_data['cl'].queryset

        response.context_data['users'] = users
        response.context_data['submissions'] = {user: {s.challenge: s for s in ChallengeSubmission.submissions_by_challenge(user)} for user in users}
        response.context_data['challenges'] = Challenge.objects.all()

        return response


def count_submissions_by_date(submissions_by_challenge, start_date):
    fmt = '%Y-%m-%d'
    submissions_by_date = {d.strftime(fmt): 0 for d in daterange(start_date, datetime.today().replace(tzinfo=start_date.tzinfo))}
    for sub_by_challenge in submissions_by_challenge:
        for sub in sub_by_challenge.submissions:
            submissions_by_date[sub.created.strftime(fmt)] += 1
    return submissions_by_date


@admin.register(EvolutionReport)
class EvolutionReportAdmin(CustomAdmin):
    class Media:
        js = ('https://cdn.plot.ly/plotly-latest.min.js', '/static/js/report/evolutionReport.js')

    change_list_template = 'admin/evolution_report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
            return response

        users = response.context_data['cl'].queryset

        submissions_by_user = {user: ChallengeSubmission.submissions_by_challenge(user) for user in users}
        earlier_submission = min([sub.created for user in users for sub_by_challenge in submissions_by_user[user] for sub in sub_by_challenge.submissions])
        submissions_by_date_user = {user: count_submissions_by_date(submissions_by_user[user], earlier_submission) for user in users if submissions_by_user[user]}
        submissions_by_date_user = {user: counts for user, counts in submissions_by_date_user.items() if counts}
        has_attempt = {user: sum(1 if len(s.submissions) > 0 else 0 for s in submissions_by_user[user]) for user in users}
        gave_up = {user: sum(1 if len(s.submissions) > 0 and s.best_result != 'OK' else 0 for s in submissions_by_user[user]) for user in users}
        ratio = {user: '-' if has_attempt[user] == 0 else '{0:.2f}%'.format(100 * gave_up[user] / has_attempt[user]) for user in users}
        response.context_data['users'] = users
        response.context_data['has_attempt'] = has_attempt
        response.context_data['gave_up'] = gave_up
        response.context_data['ratio'] = ratio
        response.context_data['submissions_by_date_user'] = submissions_by_date_user

        return response


@admin.register(TutorialsReport)
class TutorialsReportAdmin(CustomAdmin):
    change_list_template = 'admin/tutorials_report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
            return response

        users = response.context_data['cl'].queryset
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


@admin.register(ChallengesReport)
class ChallengesReportAdmin(CustomAdmin):
    class Media:
        js = ('https://cdn.plot.ly/plotly-latest.min.js', '/static/js/report/challengeReport.js')

    change_list_template = 'admin/challenges_report_change_list.html'

    def changelist_view(self, request, extra_context=None):
        ok, response = super().changelist_view(request, extra_context=extra_context)
        if not ok:
            return response

        users = response.context_data['cl'].queryset

        response.context_data['users'] = users
        sub_by_user = {}
        for user in users:
            sub_by_challenge = ChallengeSubmission.submissions_by_challenge(user)
            for submission in sub_by_challenge:
                submissions = sub_by_user.get(submission.challenge.id, [])
                submissions.append(submission.attempts)
                sub_by_user[submission.challenge.id] = submissions
        response.context_data['sub_by_challenge'] = sub_by_user

        return response
