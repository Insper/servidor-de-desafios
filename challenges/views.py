from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from challenges.code_runner import run_code

from .models import Challenge, ChallengeSubmission, Result

def create_context():
    challenges = Challenge.objects.order_by('id')
    return {'challenges': challenges}

@login_required
def index(request):
    context = create_context()
    context['submissions_by_challenge'] = ChallengeSubmission.submissions_by_challenge(request.user)
    for sbc in context['submissions_by_challenge']:
        sbc.tr_class = 'table-success' if sbc.best_result == str(Result.OK) else 'table-warning'
        sbc.success = 'Sim' if sbc.best_result == str(Result.OK) else 'Não'
    return render(request, 'challenges/index.html', context=context)

@login_required
def challenge(request, c_id):
    user = request.user
    challenge = Challenge.objects.get(pk=c_id)
    expired = False
    msg = ''
    if challenge is None:
        msg = 'Boa tentativa, mas não vai dar certo!'
    elif challenge.expire is not None and challenge.expire < timezone.now() and not user.is_staff:
        expired = True
        msg = 'Sorry... Prazo expirado!'
    if request.method == 'POST' and challenge and not expired:
        fp = request.FILES.get('code', None)
        if fp:
            answer = fp.read()
            submission = ChallengeSubmission(challenge=challenge, author=user, code=fp)

            result = run_code(challenge, answer)
            submission.failure_list = result.failure_msgs
            submission.result = Result.OK if result.success else Result.ERROR
            submission.save()

    context = create_context()
    context['challenge'] = challenge
    context['answers'] = ChallengeSubmission.objects.filter(challenge=context['challenge'], author=request.user)
    context['expired'] = expired
    context['msg'] = msg
    return render(request, 'challenges/challenge.html', context=context)