from os import replace
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from pathlib import Path
import shutil
import json
import shutil
from collections import defaultdict
from pprint import pprint

from core.models import ExercicioDeProgramacao, RespostaExProgramacao
from core.choices import Resultado


CONVERSOES = {
  'for': 'laco',
  'io': 'input',
  'loop': 'laco',
  'prova': 'variavel',
  'variaveis': 'variavel',
  'while': 'laco',
}


ORDEM_CONCEITOS = {
    'variavel': 1,
    'funcao': 2,
    'input': 3,
    'if': 4,
    'laco': 5,
    'lista': 6,
    'string': 7,
    'fatiamento': 8,
    'dicionario': 9,
    'arquivo': 10,
    'classe': 11,
}

TEMPLATE_DETAILS = '''{{
    "title": "{title}",
    "published": true,
    "terminal": true,
    "function_name": {function_name},
    "concept": "{concept}"
}}
'''

NEW_DIR = Path('new_challenge_dir')


class Command(BaseCommand):
    help = 'Converte desafios para o novo formato'

    def handle(self, *args, **kwargs):
        exercicios = ExercicioDeProgramacao.objects.all()
        for exercicio in exercicios:
            titulo = exercicio.titulo
            slug = slugify(titulo)
            challenge_path = Path(NEW_DIR, slug)

            nome_funcao = exercicio.nome_funcao
            if nome_funcao:
                nome_funcao = f'"{nome_funcao}"'
            else:
                nome_funcao = 'null'

            descricao = exercicio.descricao

            if exercicio.imagem:
                imagem_path = Path(exercicio.imagem.path)
                imagem_filename = imagem_path.name
            else:
                imagem_path = None
                imagem_filename = None
            if imagem_filename:
                descricao += f'\n\n![](raw/{slug}/{imagem_filename})'

            testes_path = Path(exercicio.testes.path)
            with open(testes_path) as f:
                testes = f.read()
            testes = testes.replace(
                    'from challenge_test_lib import challenge_test as ch', 'from strtest import str_test'
                ).replace(
                    'ch.', 'str_test.'
                ).replace(
                    'challenge_fun', 'function'
                ).replace(
                    'challenge_program', 'program'
                )

            tags = [CONVERSOES.get(t.slug, t.slug) for t in exercicio.tags.all()]
            tags = sorted(tags, key=lambda t: ORDEM_CONCEITOS[t])
            tag = tags[-1]

            detalhes = TEMPLATE_DETAILS.format(
                title=titulo,
                function_name=nome_funcao,
                concept=tag,
            )

            primeira_correta = RespostaExProgramacao.objects.filter(exercicio=exercicio, resultado=Resultado.OK).first()
            with open(primeira_correta.codigo.path) as f:
                codigo = f.read()

            # Salva tudo
            challenge_path.mkdir(parents=True, exist_ok=True)
            with open(challenge_path / 'details.json', 'w') as f:
                f.write(detalhes)
            with open(challenge_path / 'question.md', 'w') as f:
                f.write(descricao)
            with open(challenge_path / 'tests.py', 'w') as f:
                f.write(testes)
            with open(challenge_path / 'solution.py', 'w') as f:
                f.write(codigo)
            with open(challenge_path / 'wrong.py', 'w') as f:
                f.write('')
            raw_dir = challenge_path / 'raw' / slug
            raw_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(imagem_path, raw_dir / imagem_filename)

        print('Concluido')
