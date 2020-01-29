import os
from unittest import mock
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from core.models import Usuario, Turma, Matricula, RespostaExProgramacao, ExercicioDeProgramacao, Prova
from core.choices import Resultado
from core.date_utils import DateRange, tz_delta, tz_agora, tz_amanha, tz_ontem, inc_dia, dec_dia

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


def cria_aluno(i):
    return Usuario.objects.create_user(username='aluno{0}'.format(i),
                                       email='aluno{0}@email.com'.format(i),
                                       password='top_secret{0}'.format(i))


def cria_arquivo_teste():
    arquivo = mock.MagicMock(spec=File)
    arquivo.name = 'c1.py'
    return arquivo


def cria_exercicio(titulo='Hello World',
                   descricao='Escreva um programa que imprime "Olá, Mundo!"',
                   publicado=True):
    return ExercicioDeProgramacao.objects.create(titulo=titulo,
                                                 descricao=descricao,
                                                 publicado=publicado,
                                                 testes=cria_arquivo_teste())


def cria_resposta(autor,
                  exercicio,
                  resultado=Resultado.OK,
                  deletado=False,
                  data_submissao=None):
    if data_submissao is None:
        data_submissao = tz_agora()
    with mock.patch('django.utils.timezone.now',
                    mock.Mock(return_value=data_submissao)):
        resposta = RespostaExProgramacao.objects.create(autor=autor,
                                                        exercicio=exercicio,
                                                        resultado=resultado,
                                                        deletado=deletado)
    return resposta


class TurmaTestCase(TestCase):
    def setUp(self):
        anos = sorted(list(range(-1, 2)) * 2)
        inicios = [tz_delta(months=-2, years=y) for y in anos]
        fins = [tz_delta(months=+2, years=y) for y in anos]
        self.turmas = [
            Turma.objects.create(nome='turma{0}'.format(i),
                                 inicio=inicio,
                                 fim=fim)
            for i, (inicio, fim) in enumerate(zip(inicios, fins))
        ]
        # Metade dos alunos vem da turma anterior
        self.turma2aluno = {}
        alunos_por_turma = 2
        metade_turma = alunos_por_turma // 2
        self.alunos = [cria_aluno(i) for i in range(metade_turma)]
        for turma in self.turmas:
            n = len(self.alunos)
            for i in range(n, n + metade_turma):
                self.alunos.append(cria_aluno(i))
            for aluno in self.alunos[-alunos_por_turma:]:
                Matricula.objects.create(aluno=aluno, turma=turma)
                self.turma2aluno.setdefault(turma, []).append(aluno)

    def test_alunos_matriculados(self):
        todos_alunos = set(self.alunos)
        for turma in self.turmas:
            matriculados = set(self.turma2aluno[turma])
            nao_matriculados = todos_alunos - matriculados
            for aluno in matriculados:
                self.assertTrue(turma.esta_matriculado(aluno))
            for aluno in nao_matriculados:
                self.assertFalse(turma.esta_matriculado(aluno))


class ExercicioDeProgramacaoTestCase(TestCase):
    def test_lista_publicados(self):
        publicado = cria_exercicio()
        nao_publicado = cria_exercicio(
            titulo='Hello World 2',
            descricao='Escreva outro programa que imprime "Olá, Raimundo!"',
            publicado=False)
        exercicios_publicados = ExercicioDeProgramacao.objects.publicados()
        self.assertTrue(publicado in exercicios_publicados)
        self.assertTrue(nao_publicado not in exercicios_publicados)


class RespostaExProgramacaoTestCase(TestCase):
    def setUp(self):
        self.usuario = cria_aluno(1)
        self.arquivo_teste = cria_arquivo_teste()
        self.exercicio = cria_exercicio()
        self.sucesso = cria_resposta(autor=self.usuario,
                                     exercicio=self.exercicio)
        self.falha = cria_resposta(autor=self.usuario,
                                   exercicio=self.exercicio,
                                   resultado=Resultado.ERRO)

    def test_sucesso_ou_falha(self):
        self.assertTrue(self.sucesso.sucesso)
        self.assertFalse(self.falha.sucesso)

    def test_lista_de_falhas(self):
        self.falha.lista_de_falhas = []
        self.assertEqual(['Sem erros.'], self.falha.lista_de_falhas)

        falhas = ['Erro1', 'Erro2', 'Erro3']
        self.falha.lista_de_falhas = falhas
        self.assertEqual(falhas, self.falha.lista_de_falhas)

    def test_stack_traces(self):
        self.falha.stack_traces = []
        self.assertEqual(['-'], self.falha.stack_traces)

        stack_traces = ['StackTrace1', 'StackTrace2', 'StackTrace3']
        self.falha.stack_traces = stack_traces
        self.assertEqual(stack_traces, self.falha.stack_traces)

    def test_nao_inclui_deletados(self):
        deletado = cria_resposta(autor=self.usuario,
                                 exercicio=self.exercicio,
                                 resultado=Resultado.ERRO,
                                 deletado=True)
        respostas = RespostaExProgramacao.objects.all()
        self.assertTrue(self.sucesso in respostas)
        self.assertTrue(self.falha in respostas)
        self.assertTrue(deletado not in respostas)

    def test_lista_somente_do_autor(self):
        outro_aluno = cria_aluno(10)
        resposta_outro_aluno = cria_resposta(autor=outro_aluno,
                                             exercicio=self.exercicio,
                                             resultado=Resultado.OK)
        respostas = RespostaExProgramacao.objects.por(self.usuario).all()
        self.assertTrue(self.sucesso in respostas)
        self.assertTrue(self.falha in respostas)
        self.assertTrue(resposta_outro_aluno not in respostas)

    def test_conta_exercicios_por_dia(self):
        aluno = cria_aluno(10)
        amanha = tz_amanha()
        dias = 3
        comeco = tz_delta(days=-2 * (dias - 1))
        exercicios = [cria_exercicio() for _ in range(dias)]
        for i in range(dias):
            for j in range(i + 1):
                resposta = cria_resposta(autor=aluno,
                                         exercicio=exercicios[j],
                                         resultado=Resultado.OK,
                                         data_submissao=tz_delta(days=-2 * i))
        # Todos
        epd = RespostaExProgramacao.objects.por(
            aluno).conta_exercicios_por_dia()
        for d, c in zip(DateRange(comeco, amanha), [3, 0, 2, 0, 1]):
            self.assertEqual(c, epd[d.date()])
        # Últimos
        inicio = (comeco + inc_dia()).date()
        epd = RespostaExProgramacao.objects.por(
            aluno).conta_exercicios_por_dia(inicio=inicio)
        for d, c in zip(DateRange(comeco, amanha), [0, 0, 2, 0, 1]):
            self.assertEqual(c, epd[d.date()])
        # Primeiros
        fim = tz_ontem().date()
        epd = RespostaExProgramacao.objects.por(
            aluno).conta_exercicios_por_dia(fim=fim)
        for d, c in zip(DateRange(comeco, amanha), [3, 0, 2, 0, 0]):
            self.assertEqual(c, epd[d.date()])
        # Meio
        epd = RespostaExProgramacao.objects.por(
            aluno).conta_exercicios_por_dia(inicio=inicio, fim=fim)
        for d, c in zip(DateRange(comeco, amanha), [0, 0, 2, 0, 0]):
            self.assertEqual(c, epd[d.date()])

    # TODO A partir da função RespostaExProgramacaoManager.ultima_submissao não tem testes


class ProvaTestCase(TestCase):
    def test_disponivel_para(self):
        aluno_matriculado = cria_aluno(1)
        aluno_nao_matriculado = cria_aluno(2)

        inicio_turma = tz_delta(months=-2)
        fim_turma = tz_delta(months=+2)
        inicio_prova_atual = tz_delta(hours=-1)
        fim_prova_atual = tz_delta(hours=+1)
        inicio_prova_passada = tz_delta(hours=-1, months=-1)
        fim_prova_passada = tz_delta(hours=+1, months=-1)

        turma = Turma.objects.create(nome='turma1',
                                     inicio=inicio_turma,
                                     fim=fim_turma)
        Matricula.objects.create(aluno=aluno_matriculado, turma=turma)
        prova_passada = Prova.objects.create(inicio=inicio_prova_passada,
                                             fim=fim_prova_passada,
                                             titulo='Prova 1',
                                             turma=turma)
        prova_atual = Prova.objects.create(inicio=inicio_prova_atual,
                                           fim=fim_prova_atual,
                                           titulo='Prova 2',
                                           turma=turma)

        self.assertFalse(prova_passada.disponivel_para(aluno_matriculado))
        self.assertFalse(prova_passada.disponivel_para(aluno_nao_matriculado))
        self.assertTrue(prova_atual.disponivel_para(aluno_matriculado))
        self.assertFalse(prova_atual.disponivel_para(aluno_nao_matriculado))

        # Provas do aluno matriculado
        provas = Prova.objects.disponiveis_para(aluno_matriculado)
        self.assertTrue(prova_atual in provas)
        self.assertTrue(prova_passada not in provas)
        # Provas do aluno não matriculado
        provas = Prova.objects.disponiveis_para(aluno_nao_matriculado)
        self.assertTrue(prova_atual not in provas)
        self.assertTrue(prova_passada not in provas)
