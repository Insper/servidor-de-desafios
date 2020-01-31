from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import json
import shutil
from collections import defaultdict
from pprint import pprint

from core.models import Usuario, ExercicioDeProgramacao, Turma, Matricula, RespostaExProgramacao, Tag
from tutorials.models import Tutorial, AcessoAoTutorial


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
    # Criei só para facilitar na hora de implementar as funções
    # Apagar depois que estiver pronto
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
    return Usuario.objects.create_user(*args, **kwargs)


def cria_usuarios(data_dir):
    remover = ['groups', 'user_permissions', 'password']
    return cria_objs(novo_usuario, data_dir / 'users.json', remover)


def novo_ex_prog(*args, **kwargs):
    kwargs['imagem'] = kwargs['imagem'].replace('challenge', 'exercicios')
    kwargs['testes'] = kwargs['testes'].replace('challenge_tests',
                                                'arquivos_de_teste')
    return ExercicioDeProgramacao.objects.create(*args, **kwargs)


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

    shutil.copytree(data_dir / 'media', settings.MEDIA_ROOT)
    return cria_objs(novo_ex_prog, data_dir / 'challenges.json', remover,
                     traducoes)


def adiciona_tags_nos_exercicios(data_dir, exercicios, tags):
    with open(data_dir / 'tagged.json') as f:
        d_objs = json.load(f)
    for d_objs_full in d_objs:
        d_obj = d_objs_full['fields']
        ex = exercicios[d_obj['object_id']]
        ex.tags.add(tags[d_obj['tag']])
        ex.save()


def cria_tutoriais(data_dir):
    remover = ['release']
    traducoes = {
        'title': 'titulo',
        'description': 'descricao',
        'published': 'publicado'
    }
    func_instancia = Tutorial.objects.create
    return cria_objs(func_instancia, data_dir / 'tutorials.json', remover,
                     traducoes)


# TODO CHECAR DATAS E HORARIOS DEPOIS
def acesso_factory(usuarios, tutoriais):
    def novo_acesso(*args, **kwargs):
        primeiro_acesso = kwargs.pop('primeiro_acesso')
        ultimo_acesso = kwargs.pop('ultimo_acesso')

        kwargs['usuario'] = usuarios[kwargs.pop('usuario')]
        kwargs['tutorial'] = tutoriais[kwargs.pop('tutorial')]
        a = AcessoAoTutorial.objects.create(*args, **kwargs)
        AcessoAoTutorial.objects.filter(pk=a.pk).update(
            primeiro_acesso=primeiro_acesso, ultimo_acesso=ultimo_acesso)
        return a

    return novo_acesso


def cria_acessos_a_tutoriais(data_dir, usuarios, tutoriais):
    traducoes = {
        'last_access': 'ultimo_acesso',
        'access_count': 'total_acessos',
        'first_access': 'primeiro_acesso',
        'user': 'usuario',
    }

    return cria_objs(acesso_factory(usuarios, tutoriais),
                     data_dir / 'tutorial_accesses.json',
                     traducoes=traducoes)


# TODO CHECAR DATAS E HORARIOS DEPOIS
def submissao_factory(usuarios, exercicios):
    def nova_submissao(*args, **kwargs):
        data_submissao = kwargs.pop('data_submissao')

        kwargs['autor'] = usuarios[kwargs.pop('autor')]
        kwargs['exercicio'] = exercicios[kwargs.pop('exercicio')]
        kwargs['codigo'] = kwargs['codigo'].replace('upload', 'usuarios')
        r = RespostaExProgramacao.objects.create(*args, **kwargs)

        RespostaExProgramacao.objects.filter(pk=r.pk).update(
            data_submissao=data_submissao)

        return r

    return nova_submissao


def cria_submissoes(data_dir, usuarios, exercicios):
    traducoes = {
        'errors': 'erros',
        'deleted': 'deletado',
        'created': 'data_submissao',
        'code': 'codigo',
        'result': 'resultado',
        'author': 'autor',
        'challenge': 'exercicio',
    }
    return cria_objs(submissao_factory(usuarios, exercicios),
                     data_dir / 'submissions.json',
                     traducoes=traducoes)


def turma_factory(usuarios):
    def nova_turma(*args, **kwargs):
        alunos = kwargs.pop('alunos')
        t = Turma.objects.create(*args, **kwargs)
        for uid in alunos:
            m = Matricula.objects.create(aluno=usuarios[uid], turma=t)
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


def cria_tags(data_dir):
    traducoes = {'name': 'nome'}
    func_instancia = Tag.objects.create
    return cria_objs(func_instancia,
                     data_dir / 'tags.json',
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
        print('Criando usuários')
        usuarios = cria_usuarios(data_dir)
        print('Criando tags')
        tags = cria_tags(data_dir)
        print('Criando exercícios de programação')
        exercicios_de_programacao = cria_ex_prog(data_dir)
        print('Adicionando tags nos exercícios')
        adiciona_tags_nos_exercicios(data_dir, exercicios_de_programacao, tags)
        print('Criando tutoriais')
        tutoriais = cria_tutoriais(data_dir)
        print('Criando acessos a tutoriais')
        acessos_a_tutoriais = cria_acessos_a_tutoriais(data_dir, usuarios,
                                                       tutoriais)
        print('Criando submissões de exercícios')
        submissoes = cria_submissoes(data_dir, usuarios,
                                     exercicios_de_programacao)
        print('Criando turmas')
        turmas = cria_turmas(data_dir, usuarios)
        print('Concluido')
