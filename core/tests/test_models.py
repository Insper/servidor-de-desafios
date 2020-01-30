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

    def cria_varias_turmas(self):
        # Datas
        self.ano_passado = tz_delta(years=-1)
        self.dois_meses_atras = tz_delta(months=-2)
        self.mes_passado = tz_delta(months=-1)
        self.ontem = tz_ontem()
        self.hoje = tz_agora()
        self.amanha = tz_amanha()
        self.ano_que_vem = tz_delta(years=1)
        # Alunos
        self.aluno1 = cria_aluno(1)
        self.aluno2 = cria_aluno(2)
        # Turmas
        self.turma1 = cria_turma(inicio=self.dois_meses_atras, fim=self.ontem)
        self.turma2 = cria_turma(inicio=self.ano_passado, fim=self.ano_que_vem)
        self.turma3 = cria_turma(inicio=self.mes_passado, fim=self.amanha)
        self.turma4 = cria_turma()
        # Matricula
        cria_matricula(self.aluno1, self.turma1)
        cria_matricula(self.aluno1, self.turma3)
        cria_matricula(self.aluno1, self.turma4)
        cria_matricula(self.aluno2, self.turma1)
        cria_matricula(self.aluno2, self.turma2)

    def test_date_range(self):
        self.cria_varias_turmas()

        date_range1 = Turma.objects.get_date_range(self.aluno1)
        date_range2 = Turma.objects.get_date_range(self.aluno2)
        self.assertEqual(self.mes_passado.date(), date_range1.start_date)
        self.assertEqual(self.ano_passado.date(), date_range2.start_date)
        self.assertEqual(self.hoje.date(), date_range1.end_date)
        self.assertEqual(self.hoje.date(), date_range2.end_date)

    def test_lista_turmas_do_aluno(self):
        self.cria_varias_turmas()

        turmas1 = Turma.objects.do_aluno(self.aluno1)
        self.assertEqual(3, len(turmas1))
        self.assertTrue(self.turma1 in turmas1)
        self.assertTrue(self.turma3 in turmas1)
        self.assertTrue(self.turma4 in turmas1)
        turmas2 = Turma.objects.do_aluno(self.aluno2)
        self.assertEqual(2, len(turmas2))
        self.assertTrue(self.turma1 in turmas2)
        self.assertTrue(self.turma2 in turmas2)
        turmas_atuais1 = Turma.objects.atuais().do_aluno(self.aluno1)
        self.assertEqual(2, len(turmas_atuais1))
        self.assertTrue(self.turma3 in turmas_atuais1)
        self.assertTrue(self.turma4 in turmas_atuais1)
        turmas_atuais2 = Turma.objects.do_aluno(self.aluno2).atuais()
        self.assertEqual(1, len(turmas_atuais2))
        self.assertTrue(self.turma2 in turmas_atuais2)


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
