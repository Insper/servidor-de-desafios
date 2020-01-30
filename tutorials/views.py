from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Tutorial, TutorialAccess
from core.views import cria_contexto, registra_view_de_exercicios


@login_required
def tutoriais(request):
    ctx = cria_contexto(request.user)
    return render(request, 'tutorials/tutorials.html', context=ctx)


@login_required
@registra_view_de_exercicios(Tutorial)
def tutorial(request, exercicio, ctx):
    usuario = request.user

    try:
        tutorial = Tutorial.objects.get(pk=t_id)
        if not tutorial.published and not user.is_staff:
            tutorial = None
    except Tutorial.DoesNotExist:
        tutorial = None
    context['tutorial'] = tutorial
    if tutorial:
        try:
            tutorial_access = TutorialAccess.objects.get(tutorial=tutorial,
                                                         user=user)
        except TutorialAccess.DoesNotExist:
            tutorial_access = TutorialAccess(tutorial=tutorial, user=user)
        tutorial_access.access_count += 1
        tutorial_access.save()
    return render(request, 'tutorials/tutorial.html', context=context)
