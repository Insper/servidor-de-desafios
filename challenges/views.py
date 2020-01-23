from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib import messages
from datetime import datetime
from taggit.models import Tag
from challenges.code_runner import run_code
from collections import defaultdict
from itertools import zip_longest

from .models import TesteDeMesa, Challenge, ChallengeSubmission, Result, user_directory_path, Prova, stdout_list2str
from tutorials.models import Tutorial
from course.models import ChallengeBlock, get_daterange


def create_context(user):
    challenges = Challenge.all_published().order_by('id')
    testes_mesa = TesteDeMesa.objects.order_by('id')
    show_nav = True
    if user.is_staff:
        visible_challenges_ids = [c.id for c in challenges]
    else:
        classes_ids = user.class_set.values_list('id', flat=True)
        now = datetime.now()
        today = now.date()
        released_blocks = ChallengeBlock.objects.filter(Q(release_date__isnull=True) | Q(release_date__lte=today), block_class__id__in=classes_ids)
        current_tests = Prova.objects.disponiveis_para(user)
        visible_challenges_ids = set(released_blocks.values_list('challenges__id', flat=True)) | set(current_tests.values_list('exercicios__id', flat=True))
        visible_challenges = [c for c in challenges if c.id in visible_challenges_ids]
        challenges = visible_challenges

    return {'challenges': challenges, 'navtype': 'challenge', 'navitems': challenges, 'visible_challenges_ids': visible_challenges_ids, 'show_nav': show_nav, 'testes_mesa': testes_mesa}

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
    context['all_tags'] = [tag for tag in Tag.objects.all() if 'prova' not in str(tag)]
    context['submissions_per_day'] = ChallengeSubmission.objects.by(request.user).count_challenges_per_day()
    context['days'] = get_daterange(request.user)
    context['show_nav'] = False
    context['prog_tags'] = {}

    for c in context['challenges']:
        for tag in c.tags.names():
            if 'prova' in tag:
                continue
            if tag not in context['prog_tags']:
                context['prog_tags'][tag] = { "total":1,"feitos":0,"pct":0}
            else:
                context['prog_tags'][tag]['total'] += 1

    for sbc in context['submissions_by_challenge']:
        if sbc.attempts == 0:
            sbc.tr_class = 'table-light'
            sbc.success = '-'
        elif sbc.best_result == str(Result.OK):
            sbc.tr_class = 'table-success'
            sbc.success = 'Sim'
            for tag in sbc.challenge.tags.names():
                if tag in context['prog_tags']:
                    context['prog_tags'][tag]['feitos'] += 1
                    context['prog_tags'][tag]['pct'] = int((context['prog_tags'][tag]['feitos'] / context['prog_tags'][tag]['total'])*100)
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

            messages.success(request, submission.created.strftime("%d/%m/%Y %H:%M"))
            messages.success(request, submission.feedback)
            messages.success(request, submission.result)

            return redirect('challenge', c_id=c_id)

    context['challenge'] = challenge
    context['answers'] = ChallengeSubmission.objects.by(request.user).filter(challenge=context['challenge']).order_by('-created')
    context['expired'] = expired
    context['msg'] = msg
    context['latest_submission'] = ChallengeSubmission.objects.by(request.user).latest_submission(context['challenge'])
    context['error_counter'] = Counter()
    return render(request, 'challenges/challenge.html', context=context)


def name_dict2list(passo, limpa_valores=False):
    memoria = []
    if passo is None:
        return memoria
    nd = passo.name_dicts
    for contexto in sorted(nd.keys()):
        vars = nd[contexto]
        if limpa_valores:
            vars = {k: None for k in vars}
        nome_atual = contexto.split(',')[-1]
        if '<module>' in nome_atual:
            nome_atual = 'PROGRAMA'
        memoria.append((nome_atual, contexto, vars))
    return memoria


def monta_memoria(passo1, passo2):
    memoria = []
    mem1 = name_dict2list(passo1)
    mem2 = name_dict2list(passo2, True)
    for ctx1, ctx2 in zip_longest(mem1, mem2):
        if ctx1 and ctx2:
            nome_atual, contexto, vars = ctx2
            vars.update(ctx1[2])
        elif ctx1:
            nome_atual, contexto, vars = ctx1
        else:
            nome_atual, contexto, vars = ctx2
        memoria.append((nome_atual, contexto, vars))
    return memoria


def get_teste_de_mesa(request, teste_mesa, passo_atual_i):
    user = request.user
    context = create_context(user)

    # TODO Validar se o usuário tem acesso

    context['teste_mesa'] = teste_mesa
    gabarito = teste_mesa.gabarito_list
    if passo_atual_i < len(gabarito):
        # TODO TELA DE FIM: https://codepen.io/cvan/pen/LYYXzWZ
        pass
    passo_atual = gabarito[passo_atual_i]
    passo_anterior = gabarito[passo_atual_i-1] if passo_atual_i > 0 else None
    stdout = []
    if passo_anterior:
        stdout = passo_anterior.stdout
    stdout += [i for i in passo_atual.stdout[len(stdout):] if i[1] is not None]
    context['passo_atual'] = passo_atual
    context['passo_anterior'] = passo_anterior
    context['memoria'] = monta_memoria(passo_anterior, passo_atual)
    context['linhas'] = range(1, len(teste_mesa.codigo.split('\n'))+1)
    context['proxima_linha'] = passo_atual.line_i + 2
    context['stdout'] = stdout
    context['n_prev_out_lines'] = len(stdout)
    context['tem_input'] = any(out_in[1] for out_in in stdout)
    context['eh_ultimo_passo'] = passo_atual_i + 1 == len(gabarito)
    # TODO Testar com exemplo com vários prints

    return render(request, 'challenges/teste_de_mesa.html', context=context)


def extrai_memoria(post_data):
    ativos = set()
    memoria = defaultdict(lambda: dict())
    for k, v in post_data.items():
        name_data = k.split('::')
        if len(name_data) == 3:
            d_type, d_ctx, d_name = name_data
            if d_type != 'mem':
                continue
            memoria[d_ctx][d_name] = v
    return memoria


def memorias_iguais(recebido, esperado):
    # TODO Jogar essa função para o lambda (por causa do eval)
    mensagens = []
    keys = esperado.keys() | recebido.keys()
    for k in keys:
        v_esperado = esperado.get(k, {})
        v_recebido = recebido.get(k, {})
        if (not v_esperado) and v_recebido:
            mensagens.append('Alguma parte da memória não deveria estar mais ativa.')
        elif v_esperado and (not v_recebido):
            mensagens.append('A memória desativada ainda está ativa.')
        else:
            try:
                v_recebido = {r_k: eval(r_v) if r_v else None for r_k, r_v in v_recebido.items()}
                if v_esperado != v_recebido:
                    mensagens.append('Pelo menos um valor na memória está incorreto.')
            except NameError:
                mensagens.append('Não consegui entender algum dos valores da memória. Você não esqueceu as aspas em alguma string?')
    return len(mensagens) == 0, mensagens


def verifica_proxima_linha(request, gabarito, passo_atual_i):
    eh_ultimo_passo = passo_atual_i == len(gabarito) - 1
    if eh_ultimo_passo:
        return True
    prox_linha = int(request.POST.get('ctr::prox_linha', '-1'))
    return prox_linha == gabarito[passo_atual_i + 1].line_i + 1


def verifica_memoria(request, gabarito, passo_atual_i):
    passo_atual = gabarito[passo_atual_i]
    resposta = extrai_memoria(request.POST)
    esperado = passo_atual.name_dicts
    return memorias_iguais(resposta, esperado)


def verifica_terminal(request, gabarito, passo_atual_i):
    passo_anterior = None
    if passo_atual_i:
        passo_anterior = gabarito[passo_atual_i-1]
    passo_atual = gabarito[passo_atual_i]
    resposta = request.POST.get('out::terminal', '')
    prev_out_lines = int(request.POST.get('out::prev_terminal_lines', '0'))
    esperado = stdout_list2str(passo_atual.stdout[prev_out_lines:])
    return esperado == resposta


def post_teste_de_mesa(request, teste_mesa, passo_atual_i):
    gabarito = teste_mesa.gabarito_list
    assert passo_atual_i < len(gabarito)

    # TODO VALIDAR TERMINAL
    tag = 'teste-mesa'
    linha_ok = verifica_proxima_linha(request, gabarito, passo_atual_i)
    memoria_ok, mensagens = verifica_memoria(request, gabarito, passo_atual_i)
    terminal_ok = verifica_terminal(request, gabarito, passo_atual_i)
    if linha_ok and memoria_ok and terminal_ok:
        messages.success(request, 'Sem erros', extra_tags=' '.join([tag, 'text-success']))
        proximo_passo = passo_atual_i + 1
    else:
        if not linha_ok:
            messages.error(request, 'Valor incorreto para próxima linha', extra_tags=' '.join([tag, 'text-danger']))
        for msg in mensagens:
            messages.error(request, msg, extra_tags=' '.join([tag, 'text-danger']))
        if not terminal_ok:
            messages.error(request, 'Saída incorreta no terminal', extra_tags=' '.join([tag, 'text-danger']))
        proximo_passo = passo_atual_i
    return HttpResponseRedirect('{0}?passo={1}'.format(request.path_info, proximo_passo))


@login_required
def teste_de_mesa(request, pk):
    try:
        passo_atual_i = int(request.GET.get('passo', 0))
    except ValueError:
        passo_atual_i = 0
    try:
        teste_mesa = TesteDeMesa.objects.get(pk=pk)
    except TesteDeMesa.DoesNotExist:
        teste_mesa = None

    if request.method == 'POST':
        return post_teste_de_mesa(request, teste_mesa, passo_atual_i)
    else:
        return get_teste_de_mesa(request, teste_mesa, passo_atual_i)


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
        results = defaultdict(lambda: defaultdict(lambda: {}))
        if self.request.user.is_staff:
            for exercicio in self.object.exercicios.all():
                for submission in exercicio.challengesubmission_set.order_by('created'):
                    sub_dict = {
                        'created': submission.created,
                        'code': str(submission.code.url),
                    }
                    results[exercicio.title][submission.author.username] = sub_dict
            ctx['results'] = results
        return ctx

    def get_queryset(self):
        return Prova.objects.disponiveis_para(self.request.user)



@login_required
def sandbox(request):
    return render(request, 'challenges/sandbox.html', context=create_context(request.user))
