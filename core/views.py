from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from datetime import datetime
from core.code_runner import executa_codigo
from django.contrib import messages
from collections import defaultdict

from .models import Exercicio, ExercicioDeProgramacao, ExercicioProgramado, RespostaExProgramacao, Turma, Prova, Tag
from .choices import Resultado
from .models_helper import caminho_submissoes_usuario

# Constantes de contexto
EXERCICIOS = 'exercicios'
EXERCICIO = 'exercicio'
EXERCICIOS_PROGRAMADOS = 'exercicios_programados'
EXERCICIOS_PROGRAMADO = 'exercicios_programado'
ULTIMA_SUBMISSAO = 'ultima_submissao'
RESPOSTAS = 'respostas'
SHOW_NAV = 'show_nav'
SUB_POR_EX = 'submissoes_por_exercicio'
SUB_POR_DIA = 'submissoes_por_dia'
TODAS_TAGS = 'todas_tags'
DIAS = 'dias'
PROG_TAGS = 'prog_tags'
TOTAL = 'total'
FEITOS = 'feitos'
PCT = 'pct'
ERROR_COUNTER = 'error_counter'
RESULTADOS = 'resultados'


def view_do_modelo(modelo):
    view_name = settings.VIEWS_DE_EXERCICIOS.get(modelo.__name__.lower())
    if view_name is None:
        return None
    *modulo, nome = view_name.split('.')
    modulo = '.'.join(modulo)
    my_globals = globals()
    exec('from {0} import {1}'.format(modulo, nome), my_globals)
    return my_globals[nome]


def carrega_modelo_especifico(exercicios):
    return [ex.especifico() for ex in exercicios]


def cria_contexto(usuario):
    exercicios_programados = {}
    # TODO incluir exercícios de prova
    exercicios_programados = usuario.exercicios_programados_disponiveis()
    exercicios_programados = {
        e.exercicio.id: e
        for e in exercicios_programados
    }
    exercicios = usuario.exercicios_disponiveis()
    exercicios = carrega_modelo_especifico(exercicios)

    return {
        EXERCICIOS: exercicios,
        SHOW_NAV: True,
        EXERCICIOS_PROGRAMADOS: exercicios_programados,
    }


@login_required
def index(request):
    usuario = request.user
    ctx = cria_contexto(usuario)
    # if usuario.is_staff:
    #     tutoriais = Tutorial.objects.all()
    # else:
    #     tutoriais = Tutorial.all_published()
    # tutoriais = tutoriais.order_by('id')
    # ctx['tutorials'] = tutoriais
    submissoes = RespostaExProgramacao.objects.por(usuario)
    ctx.update({
        SUB_POR_EX:
        submissoes.respostas_por_exercicio(ctx['exercicios']),
        TODAS_TAGS: [
            tag for tag in Tag.objects.all()
            if 'prova' not in str(tag) and tag.exercicio_set.count()
        ],
        SUB_POR_DIA:
        submissoes.conta_exercicios_por_dia(),
        DIAS:
        Turma.objects.get_date_range(usuario),
        SHOW_NAV:
        False,
        PROG_TAGS: {},
    })

    for c in ctx[EXERCICIOS]:
        for tag in c.tags.all():
            if 'prova' in tag.nome:
                continue
            if tag not in ctx[PROG_TAGS]:
                ctx[PROG_TAGS][tag] = {TOTAL: 1, FEITOS: 0, PCT: 0}
            else:
                ctx[PROG_TAGS][tag][TOTAL] += 1

    for spe in ctx[SUB_POR_EX]:
        if spe.tentativas == 0:
            spe.tr_class = 'table-light'
            spe.success = '-'
        elif spe.melhor_resultado == Resultado.OK.label:
            spe.tr_class = 'table-success'
            spe.success = 'Sim'
            for tag in spe.exercicio.tags.all():
                if tag in ctx[PROG_TAGS]:
                    ctx[PROG_TAGS][tag][FEITOS] += 1
                    ctx[PROG_TAGS][tag][PCT] = int(
                        (ctx[PROG_TAGS][tag][FEITOS] /
                         ctx[PROG_TAGS][tag][TOTAL]) * 100)
        else:
            spe.tr_class = 'table-warning'
            spe.success = 'Não'

    return render(request, 'core/index.html', context=ctx)


class Counter:
    def __init__(self):
        self.val = 0

    def next(self):
        self.val += 1
        return ''

    def cur(self):
        return self.val


@login_required
def exercicio(request, c_id):
    usuario = request.user
    ctx = cria_contexto(usuario)

    ex = Exercicio.objects.carrega_para(c_id, usuario)

    view = view_do_modelo(ex.__class__)
    if view:
        return view(request, ex, ctx)
    raise Http404('Esse exercício não existe')


@login_required
def exercicio_de_programacao(request, exercicio, ctx):
    usuario = request.user

    # TODO Usar messages framework ao invés de colocar no contexto (na verdade acho que não está sendo utilizado atualmente)
    msg = ''
    if exercicio is None:
        msg = 'Boa tentativa, mas não vai dar certo!'
    if request.method == 'POST' and exercicio:
        codigo_arquivo = request.FILES.get('codigo_arquivo', None)
        codigo_texto = request.POST.get('codigo_texto', None)
        if codigo_texto and not codigo_arquivo:
            codigo_arquivo = ContentFile(codigo_texto.encode('utf-8'))
        if codigo_arquivo:
            codigo_texto = codigo_arquivo.read()
            submissao = RespostaExProgramacao(exercicio=exercicio,
                                              autor=usuario)

            resultado = executa_codigo(exercicio, codigo_texto)
            submissao.lista_de_falhas = resultado.failure_msgs
            submissao.stack_traces = resultado.stack_traces
            submissao.resultado = Resultado.OK if resultado.success else Resultado.ERRO
            submissao.save()
            submissao.codigo.save(caminho_submissoes_usuario(submissao, ''),
                                  codigo_arquivo)

            messages.success(
                request, submissao.data_submissao.strftime("%d/%m/%Y %H:%M"))
            messages.success(request, submissao.feedback)

            return redirect('exercicio', c_id=exercicio.id)

    ctx[EXERCICIO] = exercicio
    exercicio_programado = None
    if exercicio:
        exercicio_programado = ctx[EXERCICIOS_PROGRAMADOS].get(exercicio.id)
    ctx[EXERCICIOS_PROGRAMADO] = exercicio_programado
    ctx[RESPOSTAS] = RespostaExProgramacao.objects.por(usuario).filter(
        exercicio=ctx[EXERCICIO]).order_by('-data_submissao')
    ctx['msg'] = msg
    ctx[ULTIMA_SUBMISSAO] = RespostaExProgramacao.objects.por(
        usuario).ultima_submissao(ctx[EXERCICIO])
    ctx[ERROR_COUNTER] = Counter()
    return render(request, 'core/exercicio.html', context=ctx)


class ProvasListView(ListView):
    model = Prova

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Prova.objects.disponiveis_para(self.request.user)


class ProvaDetailView(DetailView):
    model = Prova

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        resultados = defaultdict(lambda: defaultdict(lambda: {}))
        if self.request.user.is_staff:
            for exercicio in self.object.exercicios.all():
                for submission in exercicio.respostaexprogramacao_set.order_by(
                        'data_submissao'):
                    sub_dict = {
                        'data_submissao': submission.created,
                        'codigo': str(submission.code.url),
                    }
                    resultados[exercicio.title][
                        submission.author.username] = sub_dict
            ctx[RESULTADOS] = resultados
        return ctx

    def get_queryset(self):
        return Prova.objects.disponiveis_para(self.request.user)


@login_required
def sandbox(request):
    return render(request,
                  'core/sandbox.html',
                  context=cria_contexto(request.user))
