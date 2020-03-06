import io
import csv
import zipfile
from collections import defaultdict
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from core.models import Usuario, ExercicioDeProgramacao, Turma, InteracaoUsarioExercicio, RespostaExProgramacao
from tutorials.models import Tutorial, AcessoAoTutorial
from core.date_utils import DateRange

CSV_DELIMITER = ','
LIST_DELIMITER = ';'


def cria_contexto(request):
    turmas = Turma.objects.all().order_by('nome')
    usuarios = Usuario.objects.filter(is_staff=False).exclude(
        username='aluno.teste')
    turma_filter = request.GET.get('turma', '')
    anonimo = request.GET.get('anonimo', '')

    if turma_filter:
        usuarios = usuarios.filter(matricula__turma__id=turma_filter)
    usuarios = usuarios.order_by('username')

    view_atual = request.path_info.replace('/admin/relatorio', '')

    return {
        'turmas': turmas,
        'usuarios': usuarios,
        'turma_filter': int(turma_filter) if turma_filter else -1,
        'view_atual': view_atual,
    }


@staff_member_required
def index(request):
    ctx = cria_contexto(request)
    usuarios = ctx['usuarios']
    ctx['exercicios'] = ExercicioDeProgramacao.objects.all()
    interacoes = InteracaoUsarioExercicio.objects.submissoes_por_usuario(
        usuarios)
    ctx['interacoes'] = interacoes
    return render(request, 'relatorio/index.html', ctx)


@staff_member_required
def total_por_aluno(request):
    ctx = cria_contexto(request)
    usuarios = ctx['usuarios']
    ctx['exercicios'] = ExercicioDeProgramacao.objects.all()
    ctx['total_interacoes'] = InteracaoUsarioExercicio.objects.total_por_usuario(
        usuarios).values()
    return render(request, 'relatorio/total_por_aluno.html', ctx)


def conta_subissoes_por_usuario_e_data(submissoes):
    fmt = '%Y-%m-%d'
    datas = [sub.data_submissao for sub in submissoes]
    mais_velha = min(datas)
    mais_nova = max(datas)
    submissoes_por_data_usuario = defaultdict(
        lambda: {d.strftime(fmt): 0
                 for d in DateRange(mais_velha, mais_nova)})
    for sub in submissoes:
        submissoes_por_data_usuario[sub.autor_id][sub.data_submissao.strftime(
            fmt)] += 1
    return submissoes_por_data_usuario


@staff_member_required
def evolucao(request):
    ctx = cria_contexto(request)
    usuarios = ctx['usuarios']
    submissoes = RespostaExProgramacao.objects.all()

    interacoes = InteracaoUsarioExercicio.objects.submissoes_por_usuario(
        usuarios)
    submissoes_por_data_usuario = conta_subissoes_por_usuario_e_data(
        submissoes)
    tem_tentativa = {
        u: sum(1 if ints.tentativas > 0 else 0
               for ints in interacoes[u.id].values())
        for u in usuarios
    }
    desistiu = {
        u:
        sum(1 if ints.tentativas > 0 and ints.melhor_resultado != 'OK' else 0
            for ints in interacoes[u.id].values())
        for u in usuarios
    }
    razao = {
        u:
        '-' if tem_tentativa[u] == 0 else '{0:.2f}%'.format(100 * desistiu[u] /
                                                            tem_tentativa[u])
        for u in usuarios
    }
    ctx['usuarios'] = usuarios
    ctx['tem_tentativa'] = tem_tentativa
    ctx['desistiu'] = desistiu
    ctx['razao'] = razao
    ctx['submissoes_por_data_usuario'] = submissoes_por_data_usuario

    return render(request, 'relatorio/evolucao.html', ctx)


@staff_member_required
def tutoriais(request):
    ctx = cria_contexto(request)
    usuarios = ctx['usuarios']

    tutoriais = Tutorial.objects.publicados()
    acessos = AcessoAoTutorial.objects.filter(usuario__in=usuarios,
                                              tutorial__in=tutoriais)
    acessos_por_usuario = {}
    for acesso in acessos:
        if acesso.usuario not in acessos_por_usuario:
            acessos_por_usuario[acesso.usuario] = {}
        acessos_por_usuario[acesso.usuario][
            acesso.tutorial] = acesso.total_acessos
    for usuario in usuarios:
        if usuario not in acessos_por_usuario:
            acessos_por_usuario[usuario] = {}
        for tutorial in tutoriais:
            if tutorial not in acessos_por_usuario[usuario]:
                acessos_por_usuario[usuario][tutorial] = 0

    ctx['usuarios'] = usuarios
    ctx['tutoriais'] = tutoriais
    ctx['acessos_por_usuario'] = acessos_por_usuario

    return render(request, 'relatorio/tutoriais.html', ctx)


@staff_member_required
def exercicios_de_programacao(request):
    ctx = cria_contexto(request)
    usuarios = ctx['usuarios']

    submissoes_por_exercicio = defaultdict(lambda: [])
    submissoes_por_usuario = InteracaoUsarioExercicio.objects.submissoes_por_usuario(
        usuarios)
    for interacoes in submissoes_por_usuario.values():
        for interacao in interacoes.values():
            submissoes_por_exercicio[interacao.exercicio_id].append(
                interacao.tentativas)
    ctx['submissoes_por_exercicio'] = submissoes_por_exercicio

    return render(request, 'relatorio/exercicios-de-programacao.html', ctx)


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
    # Carrega dados
    usuarios = Usuario.objects.filter(is_staff=False).exclude(
        username='aluno.teste')
    u_ids = [u.id for u in usuarios]
    submissoes = RespostaExProgramacao.objects.all()
    exercicios = ExercicioDeProgramacao.objects.publicados()

    # Cria arquivo zip
    arquivo_zip = io.BytesIO()
    with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipped:
        cabecalho_usuario = [
            'id', 'username', 'first_name', 'last_name', 'email', 'turmas'
        ]
        valores_usuario = [[
            u.id, u.username, u.first_name, u.last_name, u.email,
            LIST_DELIMITER.join(t.id for t in u.todas_turmas())
        ] for u in usuarios]
        zipped.writestr('usuarios.csv',
                        csv_str(cabecalho_usuario, valores_usuario))

        cabecalho_submissao = [
            'author_id', 'challenge_id', 'created', 'result'
        ]
        date_fmt = '%Y-%m-%d:%H:%M:%S'
        submission_values = [[
            s.author_id, s.challenge_id,
            s.created.strftime(date_fmt), s.result
        ] for s in submissions if s.author_id in user_ids]
        zipped.writestr('submissions.csv',
                        csv_str(cabecalho_submissao, submission_values))

        challenge_header = ['id', 'title', 'problem', 'tags']
        challenge_values = [[
            c.id, c.title, c.problem,
            LIST_DELIMITER.join([str(t) for t in c.tags.all()])
        ] for c in challenges]
        zipped.writestr('challenges.csv',
                        csv_str(challenge_header, challenge_values))

    arquivo_zip.seek(0)
    response = HttpResponse(arquivo_zip, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=report_data.zip'
    return response


@staff_member_required
def situacao(request):
    turma_selecionada = request.GET.get('turma')
    aluno_selecionado = request.GET.get('aluno')

    dados_do_aluno = []
    if aluno_selecionado is not None and aluno_selecionado != 'Todos':
        dados_do_aluno = [Usuario.objects.get(username=aluno_selecionado)]
    if not dados_do_aluno and turma_selecionada is not None and turma_selecionada != 'Todas':
        dados_do_aluno = [
            u for u in Turma.objects.get(nome=turma_selecionada).alunos()
        ]

    dias = []
    if dados_do_aluno:
        dias = Turma.objects.get_date_range(dados_do_aluno[0])

    submissoes_por_dia_usuario = {
        u: RespostaExProgramacao.objects.por(u).conta_exercicios_por_dia()
        for u in dados_do_aluno
    }
    ctx = {
        'turma_selecionada':
        turma_selecionada,
        'aluno_selecionado':
        aluno_selecionado,
        'dados_do_aluno':
        dados_do_aluno,
        'submissoes_por_dia_usuario':
        submissoes_por_dia_usuario,
        'turmas':
        Turma.objects.all(),
        'alunos':
        Usuario.objects.filter(is_staff=False).exclude(
            username='aluno.teste').order_by('username'),
        'dias':
        dias,
    }
    return render(request, 'relatorio/situacao.html', ctx)
