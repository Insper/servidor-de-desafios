import os
import unittest.mock as mock
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from core.models import Usuario, Turma, Matricula, RespostaExProgramacao, ExercicioDeProgramacao, Prova
from core.choices import Resultado

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


def novo_aluno(i):
    return Usuario.objects.create_user(username='aluno{0}'.format(i),
                                       email='aluno{0}@email.com'.format(i),
                                       password='top_secret{0}'.format(i))


class TurmaTestCase(TestCase):
    def setUp(self):
        hoje = timezone.now().date()
        anos = sorted(list(range(-1, 2)) * 2)
        inicios = [hoje + relativedelta(months=-2, years=y) for y in anos]
        fins = [hoje + relativedelta(months=+2, years=y) for y in anos]
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
        self.alunos = [novo_aluno(i) for i in range(metade_turma)]
        for turma in self.turmas:
            n = len(self.alunos)
            for i in range(n, n + metade_turma):
                self.alunos.append(novo_aluno(i))
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


class RespostaExProgramacaoTestCase(TestCase):
    def setUp(self):
        self.usuario = novo_aluno(1)
        self.arquivo_teste = mock.MagicMock(spec=File)
        self.arquivo_teste.name = 'c1.py'
        self.exercicio = ExercicioDeProgramacao.objects.create(
            titulo='Hello World',
            descricao='Escreva um programa que imprime "Olá, Mundo!"',
            publicado=True,
            testes=self.arquivo_teste)
        self.sucesso = RespostaExProgramacao.objects.create(
            autor=self.usuario,
            exercicio=self.exercicio,
            resultado=Resultado.OK)
        self.falha = RespostaExProgramacao.objects.create(
            autor=self.usuario,
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


class ProvaTestCase(TestCase):
    def test_disponivel_para(self):
        aluno_matriculado = novo_aluno(1)
        aluno_nao_matriculado = novo_aluno(2)

        hoje = timezone.now()
        inicio_turma = hoje + relativedelta(months=-2)
        fim_turma = hoje + relativedelta(months=+2)
        inicio_prova_atual = hoje + relativedelta(hours=-1)
        fim_prova_atual = hoje + relativedelta(hours=+1)
        inicio_prova_passada = hoje + relativedelta(hours=-1, months=-1)
        fim_prova_passada = hoje + relativedelta(hours=+1, months=-1)

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
