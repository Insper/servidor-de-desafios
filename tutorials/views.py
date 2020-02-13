from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.models import InteracaoUsarioExercicio
from core.choices import Resultado
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

    try:
        slide_i = int(request.GET.get('slide', 0))
    except ValueError:
        slide_i = 0
    slides = tutorial.slides_html
    if slide_i == -1:
        slide_html = tutorial.todos_slides_html
    else:
        try:
            slide_html = slides[slide_i]
        except IndexError:
            slide_html = slides[0]
            slide_i = 0

    ctx['tutorial'] = tutorial
    ctx['slide_html'] = slide_html
    ctx['slide_i'] = slide_i
    ctx['prev_slide'] = slide_i - 1 if slide_i > 0 else None
    ctx['next_slide'] = slide_i + 1 if slide_i >= 0 and slide_i < len(
        slides) - 1 else None
    ctx['mostrar_tudo'] = (slide_i == -1)

    if tutorial:
        try:
            acesso = AcessoAoTutorial.objects.get(tutorial=tutorial,
                                                  usuario=usuario)
        except AcessoAoTutorial.DoesNotExist:
            acesso = AcessoAoTutorial(tutorial=tutorial, usuario=usuario)
        acesso.total_acessos += 1
        acesso.save()

        try:
            interacao = InteracaoUsarioExercicio.objects.get(
                exercicio=tutorial, usuario=usuario)
        except InteracaoUsarioExercicio.DoesNotExist:
            interacao = InteracaoUsarioExercicio(exercicio=tutorial,
                                                 usuario=usuario)
        interacao.tentativas += 1
        try:
            slide_i = int(request.GET.get('slide', 0))
        except ValueError:
            slide_i = 0
        if slide_i == -1 or slide_i == tutorial.total_slides - 1:
            interacao.melhor_resultado = Resultado.OK
        interacao.save()

    return render(request, 'tutorials/tutorial.html', context=ctx)
