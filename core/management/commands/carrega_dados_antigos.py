from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import json
import shutil
from pprint import pprint

from core.models import Usuario, ExercicioDeProgramacao, Turma, Matricula
from tutorials.models import Tutorial


def limpa(d, campos_remover, t):
    for remover in campos_remover:
        try:
            del d[remover]
        except KeyError:
            pass
    return {t(k): v for k, v in d.items()}


def cria_tradutor(traducoes):
    if traducoes is None:
        traducoes = {}

    def t(palavra):
        try:
            return traducoes[palavra]
        except KeyError:
            return palavra

    return t


def lista_campos(filename):
    with open(filename) as f:
        d_objs = json.load(f)
    campos = set()
    for d_objs_full in d_objs:
        pk = d_objs_full['pk']
        campos |= set(d_objs_full['fields'].keys())
    return campos


def cria_objs(func_instancia, filename, remover=None, traducoes=None):
    if remover is None:
        remover = []
    t = cria_tradutor(traducoes)
    objs = {}
    with open(filename) as f:
        d_objs = json.load(f)
    for d_objs_full in d_objs:
        pk = d_objs_full['pk']
        d_obj = limpa(d_objs_full['fields'], remover, t)
        instancia = func_instancia(**d_obj)
        objs[pk] = instancia
    return objs


def novo_usuario(*args, **kwargs):
    kwargs['password'] = kwargs['username']
    # TODO Usar Usuario.objects.create_user(*args, **kwargs)
    return Usuario(*args, **kwargs)


def cria_usuarios(data_dir):
    remover = ['groups', 'user_permissions', 'password']
    return cria_objs(novo_usuario, data_dir / 'users.json', remover)


def novo_ex_prog(*args, **kwargs):
    kwargs['imagem'] = kwargs['imagem'].replace('challenge', 'exercicios')
    kwargs['testes'] = kwargs['testes'].replace('challenge_tests',
                                                'arquivos_de_teste')
    # return ExercicioDeProgramacao.objects.create(*args, **kwargs)
    return ExercicioDeProgramacao(*args, **kwargs)


def cria_ex_prog(data_dir):
    remover = ['expire', 'release']
    traducoes = {
        'function_name': 'nome_funcao',
        'image': 'imagem',
        'problem': 'descricao',
        'published': 'publicado',
        'test_file': 'testes',
        'title': 'titulo',
    }
    # shutil.copytree(data_dir / 'media', settings.MEDIA_ROOT)
    return cria_objs(novo_ex_prog, data_dir / 'challenges.json', remover,
                     traducoes)


def cria_tutoriais(data_dir):
    remover = ['release']
    traducoes = {
        'title': 'titulo',
        'description': 'descricao',
        'published': 'publicado'
    }
    # func_instancia = Tutorial.objects.create
    func_instancia = Tutorial
    return cria_objs(func_instancia, data_dir / 'tutorials.json', remover,
                     traducoes)


def turma_factory(usuarios):
    def nova_turma(*args, **kwargs):
        alunos = kwargs['alunos']
        del kwargs['alunos']
        # Turma.objects.create
        t = Turma(*args, **kwargs)
        for uid in alunos:
            # Matricula.objects.create
            m = Matricula(aluno=usuarios[uid], turma=t)
        return t

    return nova_turma


def cria_turmas(data_dir, usuarios):
    traducoes = {
        'name': 'nome',
        'start_date': 'inicio',
        'end_date': 'fim',
        'students': 'alunos',
    }
    return cria_objs(turma_factory(usuarios),
                     data_dir / 'classes.json',
                     traducoes=traducoes)


class Command(BaseCommand):
    help = 'Carrega dados da versão anterior do servidor'

    def add_arguments(self, parser):
        parser.add_argument(
            'data_dir',
            type=str,
            help='Indica o diretório contendo os dados a serem carregados')

    def handle(self, *args, **kwargs):
        data_dir = Path(kwargs['data_dir'])
        usuarios = cria_usuarios(data_dir)
        exercicios_de_programacao = cria_ex_prog(data_dir)
        tutoriais = cria_tutoriais(data_dir)
        turmas = cria_turmas(data_dir, usuarios)
        print(tutoriais)
