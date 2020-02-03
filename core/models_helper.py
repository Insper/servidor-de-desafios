from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
import os

# Constantes
FEEDBACK_SEP = '|||'
STACKTRACE_SEP = '<|>|<|>'
STACKTRACE_FILE_PATTERN = 'File "<string>", '
# Caminhos
DIR_TESTES = 'arquivos_de_teste/'
DIR_USUARIOS = 'usuarios/'
DIR_EXERCICIOS = 'exercicios/'

CODIGO_TESTE_DEFAULT = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    TIMEOUT = 1

    @challenge_test.error_message('Erro no servidor')
    def test_1(self):
        self.assertTrue(True)
'''


def criar_arquivo_de_testes_padrao():
    now = timezone.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
    filename = os.path.join(DIR_TESTES, 'test_{0}.py'.format(now))
    path = default_storage.save(filename, ContentFile(CODIGO_TESTE_DEFAULT))
    return path


def caminho_submissoes_usuario(instance, filename):
    # O arquivo será enviado para MEDIA_ROOT/user_<id>/<filename>
    username = instance.autor.username
    id = instance.exercicio.id
    data_criacao = instance.data_submissao.strftime('%Y_%m_%d_%H_%M_%S_%f')
    filename = 'user_{0}/ch{1}_{2}.py'.format(username, id, data_criacao)
    return os.path.join(DIR_USUARIOS, filename)


def escape_js(string):
    replacements = {
        #'\\': '\\\\',  # TODO this line makes everything become a single line (escapes all \n)
        '\n': '\\n',
        '\r': '',
        '"': '\\\"',
    }
    for k, v in replacements.items():
        string = string.replace(k, v)
    return string
