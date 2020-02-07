from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from itertools import zip_longest
from collections import defaultdict

from .models import stdout_list2str


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


def get_teste_de_mesa(request, teste_mesa, passo_atual_i, context):
    user = request.user

    # TODO Validar se o usuário tem acesso

    context['teste_mesa'] = teste_mesa
    gabarito = teste_mesa.gabarito_list
    if passo_atual_i >= len(gabarito):
        # TODO TELA DE FIM: https://codepen.io/cvan/pen/LYYXzWZ
        context['teste_concluido'] = True
    else:
        passo_atual = gabarito[passo_atual_i]
        passo_anterior = gabarito[passo_atual_i -
                                  1] if passo_atual_i > 0 else None
        stdout = []
        if passo_anterior:
            stdout = passo_anterior.stdout
        stdout += [
            i for i in passo_atual.stdout[len(stdout):] if i[1] is not None
        ]
        context['passo_atual'] = passo_atual
        context['passo_anterior'] = passo_anterior
        context['memoria'] = monta_memoria(passo_anterior, passo_atual)
        context['linhas'] = range(1, len(teste_mesa.codigo.split('\n')) + 1)
        context['proxima_linha'] = passo_atual.line_i + 2
        context['stdout'] = stdout
        context['n_prev_out_lines'] = len(stdout)
        context['tem_input'] = any(out_in[1] for out_in in stdout)
        context['eh_ultimo_passo'] = passo_atual_i + 1 == len(gabarito)
        context['teste_concluido'] = False
        # TODO Testar com exemplo com vários prints

    return render(request, 'teste_de_mesa/teste_de_mesa.html', context=context)


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
            mensagens.append(
                'Alguma parte da memória não deveria estar mais ativa.')
        elif v_esperado and (not v_recebido):
            mensagens.append('A memória desativada ainda está ativa.')
        else:
            try:
                v_recebido = {
                    r_k: eval(r_v) if r_v else None
                    for r_k, r_v in v_recebido.items()
                }
                if v_esperado != v_recebido:
                    mensagens.append(
                        'Pelo menos um valor na memória está incorreto.')
            except NameError:
                mensagens.append(
                    'Não consegui entender algum dos valores da memória. Você não esqueceu as aspas em alguma string?'
                )
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
        passo_anterior = gabarito[passo_atual_i - 1]
    passo_atual = gabarito[passo_atual_i]
    resposta = request.POST.get('out::terminal', '')
    prev_out_lines = int(request.POST.get('out::prev_terminal_lines', '0'))
    esperado = stdout_list2str(passo_atual.stdout[prev_out_lines:])
    return esperado == resposta


def post_teste_de_mesa(request, teste_mesa, passo_atual_i):
    gabarito = teste_mesa.gabarito_list
    assert passo_atual_i < len(gabarito)

    tag = 'teste-mesa'
    linha_ok = verifica_proxima_linha(request, gabarito, passo_atual_i)
    memoria_ok, mensagens = verifica_memoria(request, gabarito, passo_atual_i)
    terminal_ok = verifica_terminal(request, gabarito, passo_atual_i)
    if linha_ok and memoria_ok and terminal_ok:
        messages.success(request,
                         'Sem erros',
                         extra_tags=' '.join([tag, 'text-success']))
        proximo_passo = passo_atual_i + 1
    else:
        if not linha_ok:
            messages.error(request,
                           'Valor incorreto para próxima linha',
                           extra_tags=' '.join([tag, 'text-danger']))
        for msg in mensagens:
            messages.error(request,
                           msg,
                           extra_tags=' '.join([tag, 'text-danger']))
        if not terminal_ok:
            messages.error(request,
                           'Saída incorreta no terminal',
                           extra_tags=' '.join([tag, 'text-danger']))
        proximo_passo = passo_atual_i
    return HttpResponseRedirect('{0}?passo={1}'.format(request.path_info,
                                                       proximo_passo))


@login_required
def teste_de_mesa(request, teste_mesa, ctx):
    try:
        passo_atual_i = int(request.GET.get('passo', 0))
    except ValueError:
        passo_atual_i = 0

    if request.method == 'POST':
        return post_teste_de_mesa(request, teste_mesa, passo_atual_i)
    else:
        return get_teste_de_mesa(request, teste_mesa, passo_atual_i, ctx)
