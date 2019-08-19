import io
import csv
import zipfile
from collections import defaultdict
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from challenges.models import Challenge, ChallengeSubmission
from tutorials.models import Tutorial, TutorialAccess
from course.models import Class
from .models import *


CSV_DELIMITER = ','
LIST_DELIMITER = ';'


def make_context(request):
    classes = Class.objects.all().order_by('name')
    users = User.objects.filter(is_staff=False).exclude(username='aluno.teste')
    class_filter = request.GET.get('class', '')

    if class_filter:
        users = users.filter(class__id__exact=class_filter)
    users = users.order_by('username')

    current_view = request.path_info.replace('/admin/report', '')

    return {
        'classes': classes,
        'users': users,
        'class_filter': int(class_filter) if class_filter else -1,
        'current_view': current_view,
    }


@staff_member_required
def index(request):
    context = make_context(request)
    users = context['users']
    context['challenges'] = Challenge.objects.all()
    challenge_reports = UserChallengeReport.objects.all()
    context['user_challenges'] = UserChallengeReport.submissions_by_user(users)
    return render(request, 'report/index.html', context)


def count_submissions_by_date(submissions_by_challenge):
    fmt = '%Y-%m-%d'
    submissions_by_date = defaultdict(lambda: 0)
    for submission_report in submissions_by_challenge.values():
        submissions_by_date[sub.created.strftime(fmt)] += 1
    return submissions_by_date


def count_submissions_by_user_and_date(submissions):
    fmt = '%Y-%m-%d'
    sub_dates = [sub.created for sub in submissions]
    earlier_submission = min(sub_dates)
    latest_submission = max(sub_dates)
    submissions_by_date_user = defaultdict(lambda: {d.strftime(fmt): 0 for d in daterange(earlier_submission, latest_submission)})
    for submission in submissions:
        submissions_by_date_user[submission.author_id][submission.created.strftime(fmt)] += 1
    return submissions_by_date_user


@staff_member_required
def evolution(request):
    context = make_context(request)
    users = context['users']
    submissions = ChallengeSubmission.objects.all()

    submissions_by_user = UserChallengeReport.submissions_by_user(users)
    submissions_by_date_user = count_submissions_by_user_and_date(submissions)
    #submissions_by_date_user = {user: count_submissions_by_date(submissions_by_user[user]) for user in users if submissions_by_user[user]}
    #submissions_by_date_user = {user: counts for user, counts in submissions_by_date_user.items() if counts}
    has_attempt = {user: sum(1 if s.attempts > 0 else 0 for s in submissions_by_user[user.id].values()) for user in users}
    gave_up = {user: sum(1 if s.attempts > 0 and s.best_result != 'OK' else 0 for s in submissions_by_user[user.id].values()) for user in users}
    ratio = {user: '-' if has_attempt[user] == 0 else '{0:.2f}%'.format(100 * gave_up[user] / has_attempt[user]) for user in users}
    context['users'] = users
    context['has_attempt'] = has_attempt
    context['gave_up'] = gave_up
    context['ratio'] = ratio
    context['submissions_by_date_user'] = submissions_by_date_user

    return render(request, 'report/evolution.html', context)


@staff_member_required
def tutorials(request):
    context = make_context(request)
    users = context['users']

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

    context['users'] = users
    context['tutorials'] = tutorials
    context['accesses_by_user'] = accesses_by_user

    return render(request, 'report/tutorials.html', context)


@staff_member_required
def challenges(request):
    context = make_context(request)
    users = context['users']

    sub_by_challenge = defaultdict(lambda: [])
    submissions_by_user = UserChallengeReport.submissions_by_user(users)
    for user_report in submissions_by_user.values():
        for user_challenge_report in user_report.values():
            sub_by_challenge[user_challenge_report.challenge_id].append(user_challenge_report.attempts)
    context['sub_by_challenge'] = sub_by_challenge

    return render(request, 'report/challenges.html', context)


def csv_str(header, values):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=CSV_DELIMITER)
    writer.writerow(header)
    for row in values:
        writer.writerow(row)
    return str(output.getvalue())
    output.seek(0)
    return output.read()


@staff_member_required
def download(request):
    # Load data
    users = User.objects.filter(is_staff=False).exclude(username='aluno.teste')
    user_ids = [user.id for user in users]
    submissions = ChallengeSubmission.objects.all()
    challenges = Challenge.all_published()

    # Create the zip file
    zipped_file = io.BytesIO()
    with zipfile.ZipFile(zipped_file, 'w', zipfile.ZIP_DEFLATED) as zipped:
        user_header = ['id', 'username', 'first_name', 'last_name', 'email', 'classes']
        user_values = [[u.id, u.username, u.first_name, u.last_name, u.email, LIST_DELIMITER.join(c.name for c in u.class_set.all())] for u in users]
        zipped.writestr('users.csv', csv_str(user_header, user_values))

        submission_header = ['author_id', 'challenge_id', 'created', 'result']
        date_fmt = '%Y-%m-%d:%H:%M:%S'
        submission_values = [[s.author_id, s.challenge_id, s.created.strftime(date_fmt), s.result] for s in submissions if s.author_id in user_ids]
        zipped.writestr('submissions.csv', csv_str(submission_header, submission_values))

        challenge_header = ['id', 'title', 'problem', 'tags']
        challenge_values = [[c.id, c.title, c.problem, LIST_DELIMITER.join([str(t) for t in c.tags.all()])] for c in challenges]
        zipped.writestr('challenges.csv', csv_str(challenge_header, challenge_values))

    zipped_file.seek(0)
    response = HttpResponse(zipped_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=report_data.zip'
    return response


@staff_member_required
def status(request):
    selected_course = request.GET.get('turma')
    selected_student = request.GET.get('aluno')

    student_data = []
    if selected_student is not None and selected_student != 'Todos':
        student_data = [User.objects.get(username=selected_student)]
    if student_data is None and selected_course:
        student_data = Class.objects.get(name=selected_course).students.all()

    user_submissions_per_day = {u: ChallengeSubmission.objects.by(u).count_challenges_per_day() for u in student_data}
    context = {
        'selectedClass': selected_course,
        'selectedStudent': selected_student,
        'student_data': student_data,
        'user_submissions_per_day': user_submissions_per_day,
        'classes': Class.objects.all(),
        'students': User.objects.filter(is_staff=False).exclude(username='aluno.teste'),
    }
    return render(request, 'report/status.html', context)
