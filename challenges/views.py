from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
from datetime import datetime
from taggit.models import Tag
from challenges.code_runner import run_code

from .models import Challenge, ChallengeSubmission, Result, user_directory_path
from tutorials.models import Tutorial
from course.models import ChallengeBlock, get_daterange


def create_context(user):
    challenges = Challenge.all_published().order_by('id')
    show_nav = True
    if user.is_staff:
        visible_challenges_ids = [c.id for c in challenges]
    else:
        classes_ids = user.class_set.values_list('id', flat=True)
        today = datetime.now().date()
        released_blocks = ChallengeBlock.objects.filter(Q(release_date__isnull=True) | Q(release_date__lte=today), block_class__id__in=classes_ids)
        visible_challenges_ids = set(released_blocks.values_list('challenges__id', flat=True))
        visible_challenges = [c for c in challenges if c.id in visible_challenges_ids]
        challenges = visible_challenges
        
    return {'challenges': challenges, 'navtype': 'challenge', 'navitems': challenges, 'visible_challenges_ids': visible_challenges_ids, 'show_nav': show_nav}


@login_required
def index(request):
    context = create_context(request.user)
    if request.user.is_staff:
        tutorials = Tutorial.objects.all()
    else:
        tutorials = Tutorial.all_published()
    tutorials = tutorials.order_by('id')
    context['tutorials'] = tutorials
    context['submissions_by_challenge'] = ChallengeSubmission.objects.by(request.user).submissions_by_challenge(context['visible_challenges_ids'])
    context['all_tags'] = Tag.objects.all()
    context['submissions_per_day'] = ChallengeSubmission.objects.by(request.user).count_challenges_per_day()
    context['days'] = get_daterange(request.user)
    context['show_nav'] = False
    for sbc in context['submissions_by_challenge']:
        if sbc.attempts == 0:
            sbc.tr_class = 'table-light'
            sbc.success = '-'
        elif sbc.best_result == str(Result.OK):
            sbc.tr_class = 'table-success'
            sbc.success = 'Sim'
        else:
            sbc.tr_class = 'table-warning'
            sbc.success = 'Não'
    return render(request, 'challenges/index.html', context=context)

class Counter:
    def __init__(self):
        self.val = 0

    def next(self):
        self.val += 1
        return ''

    def cur(self):
        return self.val

@login_required
def challenge(request, c_id):
    user = request.user
    context = create_context(user)

    challenge = None
    if c_id in context['visible_challenges_ids']:
        try:
            challenge = Challenge.objects.get(pk=c_id)
            if not challenge.published and not user.is_staff:
                challenge = None
        except Challenge.DoesNotExist:
            challenge = None
    expired = False
    msg = ''
    if challenge is None:
        msg = 'Boa tentativa, mas não vai dar certo!'
    elif challenge.expire is not None and challenge.expire < timezone.now() and not user.is_staff:
        expired = True
        msg = 'Sorry... Prazo expirado!'
    if request.method == 'POST' and challenge and not expired:
        fp = request.FILES.get('code', None)
        answer = request.POST.get('codetext', None)
        if answer and not fp:
            fp = ContentFile(answer.encode('utf-8'))
        if fp:
            answer = fp.read()
            submission = ChallengeSubmission(challenge=challenge, author=user)

            result = run_code(challenge, answer)
            submission.failure_list = result.failure_msgs
            submission.stack_traces = result.stack_traces
            submission.result = Result.OK if result.success else Result.ERROR
            submission.save()
            submission.code.save(user_directory_path(submission, ''), fp)
            return redirect('challenge', c_id=c_id)

    context['challenge'] = challenge
    context['answers'] = ChallengeSubmission.objects.by(request.user).filter(challenge=context['challenge']).order_by('-created')
    context['expired'] = expired
    context['msg'] = msg
    context['latest_submission'] = ChallengeSubmission.objects.by(request.user).latest_submission(context['challenge'])
    context['error_counter'] = Counter()
    return render(request, 'challenges/challenge.html', context=context)

@login_required
def sandbox(request):
    return render(request, 'challenges/sandbox.html', context=create_context(request.user))
