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

from teste_de_mesa.models import TesteDeMesa
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
    "concept": "{concept}"
}}
'''

NEW_DIR = Path('new_trace_dir')


class Command(BaseCommand):
    help = 'Converte testes de mesa para o novo formato'

    def handle(self, *args, **kwargs):
        exercicios = TesteDeMesa.objects.all()
        for exercicio in exercicios:
            titulo = exercicio.titulo
            slug = slugify(titulo)
            challenge_path = Path(NEW_DIR, slug)

            codigo = exercicio.codigo
            gabarito = exercicio.gabarito

            tags = [CONVERSOES.get(t.slug, t.slug) for t in exercicio.tags.all()]
            tags = sorted(tags, key=lambda t: ORDEM_CONCEITOS[t])
            tag = tags[-1]

            detalhes = TEMPLATE_DETAILS.format(
                title=titulo,
                concept=tag,
            )

            # Salva tudo
            challenge_path.mkdir(parents=True, exist_ok=True)
            with open(challenge_path / 'details.json', 'w') as f:
                f.write(detalhes)
            with open(challenge_path / 'code.py', 'w') as f:
                f.write(codigo)
            with open(challenge_path / 'trace.json', 'w') as f:
                f.write(gabarito)

        print('Concluido')
