from django.core.files import File
from unittest import mock

from core.models import Usuario, Turma, Matricula, RespostaExProgramacao, ExercicioDeProgramacao, Prova
from core.choices import Resultado
from core.date_utils import *


def cria_aluno(i):
    return Usuario.objects.create_user(username='aluno{0}'.format(i),
                                       email='aluno{0}@email.com'.format(i),
                                       password='top_secret{0}'.format(i))


def cria_turma(nome='', inicio=None, fim=None):
    return Turma.objects.create(nome=nome, inicio=inicio, fim=fim)


def cria_turma_atual(nome=''):
    inicio = tz_delta(months=-2)
    fim = tz_delta(months=2)
    return cria_turma(nome, inicio, fim)


def cria_matricula(aluno, turma):
    return Matricula.objects.create(aluno=aluno, turma=turma)


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
