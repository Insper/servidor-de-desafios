import os
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from core.models import Usuario, Turma, Matricula, RespostaExProgramacao, ExercicioDeProgramacao, Prova
from core.choices import Resultado
from core.date_utils import *
from .factories import *

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


class TurmaTestCase(TestCase):
    def test_alunos_matriculados(self):
        anos = sorted(list(range(-1, 2)) * 2)
        inicios = [tz_delta(months=-2, years=y) for y in anos]
        fins = [tz_delta(months=+2, years=y) for y in anos]
        turmas = [
            cria_turma(nome='turma{0}'.format(i), inicio=inicio, fim=fim)
            for i, (inicio, fim) in enumerate(zip(inicios, fins))
        ]
        # Metade dos alunos vem da turma anterior
        turma2aluno = {}
        alunos_por_turma = 2
        metade_turma = alunos_por_turma // 2
        alunos = [cria_aluno(i) for i in range(metade_turma)]
        for turma in turmas:
            n = len(alunos)
            for i in range(n, n + metade_turma):
                alunos.append(cria_aluno(i))
            for aluno in alunos[-alunos_por_turma:]:
                cria_matricula(aluno=aluno, turma=turma)
                turma2aluno.setdefault(turma, []).append(aluno)

        todos_alunos = set(alunos)
        for turma in turmas:
            matriculados = set(turma2aluno[turma])
            nao_matriculados = todos_alunos - matriculados
            for aluno in matriculados:
                self.assertTrue(turma.esta_matriculado(aluno))
            for aluno in nao_matriculados:
                self.assertFalse(turma.esta_matriculado(aluno))

    def test_date_range(self):
        # Datas
        ano_passado = tz_delta(years=-1)
        dois_meses_atras = tz_delta(months=-2)
        mes_passado = tz_delta(months=-1)
        ontem = tz_ontem()
        hoje = tz_agora()
        amanha = tz_amanha()
        ano_que_vem = tz_delta(years=1)
        # Alunos
        aluno1 = cria_aluno(1)
        aluno2 = cria_aluno(2)
        # Turmas
        turma1 = cria_turma(inicio=dois_meses_atras, fim=ontem)
        turma2 = cria_turma(inicio=ano_passado, fim=ano_que_vem)
        turma3 = cria_turma(inicio=mes_passado, fim=amanha)
        turma4 = cria_turma()
        # Matricula
        cria_matricula(aluno1, turma1)
        cria_matricula(aluno1, turma3)
        cria_matricula(aluno1, turma4)
        cria_matricula(aluno2, turma1)
        cria_matricula(aluno2, turma2)
        # Asserts
        date_range1 = Turma.objects.get_date_range(aluno1)
        date_range2 = Turma.objects.get_date_range(aluno2)
        self.assertEqual(mes_passado.date(), date_range1.start_date)
        self.assertEqual(ano_passado.date(), date_range2.start_date)
        self.assertEqual(hoje.date(), date_range1.end_date)
        self.assertEqual(hoje.date(), date_range2.end_date)


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

        turma = cria_turma(nome='turma1', inicio=inicio_turma, fim=fim_turma)
        cria_matricula(aluno=aluno_matriculado, turma=turma)
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
