from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Tutorial, AcessoAoTutorial
from core.views import cria_contexto


@login_required
def tutoriais(request):
    ctx = cria_contexto(request.user)
    ctx['tutorials'] = Tutorial.objects.disponiveis_para(request.user)
    return render(request, 'tutorials/tutorials.html', context=ctx)


@login_required
def tutorial(request, tutorial, ctx):
    usuario = request.user

    ctx['tutorial'] = tutorial
    if tutorial:
        try:
            acesso = AcessoAoTutorial.objects.get(tutorial=tutorial,
                                                  usuario=usuario)
        except AcessoAoTutorial.DoesNotExist:
            acesso = AcessoAoTutorial(tutorial=tutorial, usuario=usuario)
        acesso.total_acessos += 1
        acesso.save()
    return render(request, 'tutorials/tutorial.html', context=ctx)
