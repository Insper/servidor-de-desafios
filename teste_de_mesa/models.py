from collections import namedtuple
from django.db import models
import json

from .validators import json_validator
from .managers import InteracaoUsuarioPassoTesteDeMesaManager
from core.models import Exercicio, RespostaSubmetida, InteracaoUsarioExercicio
from core.choices import Resultado


class NonStrippingTextField(models.TextField):
    """
    A TextField that does not strip whitespace at the beginning/end of
    it's value.  Might be important for markup/code.
    Source: https://stackoverflow.com/a/40709539
    """
    def formfield(self, **kwargs):
        kwargs['strip'] = False
        return super(NonStrippingTextField, self).formfield(**kwargs)


def stdout_list2str(stdout_list):
    return '\n'.join(
        (''.join((i for i in out_in if i)) for out_in in stdout_list))


_TraceData = namedtuple('TraceData',
                        'line_i,line,name_dicts,call_line_i,retval,stdout')


class TraceData(_TraceData):
    @property
    def stdout_str(self):
        return stdout_list2str(self.stdout)


class TesteDeMesa(Exercicio):
    codigo = NonStrippingTextField(blank=False)
    gabarito = models.TextField(blank=False, validators=(json_validator, ))

    class Meta:
        verbose_name_plural = 'testes de mesa'

    @property
    def titulo_completo(self):
        return '[TESTE DE MESA] {0}'.format(self.titulo)

    @property
    def gabarito_list(self):
        return [TraceData(*i) for i in json.loads(self.gabarito)]


class RespostaTesteDeMesa(RespostaSubmetida):
    resultado_linha = models.CharField(max_length=2,
                                       choices=Resultado.choices,
                                       blank=True)
    resultado_memoria = models.CharField(max_length=2,
                                         choices=Resultado.choices,
                                         blank=True)
    resultado_terminal = models.CharField(max_length=2,
                                          choices=Resultado.choices,
                                          blank=True)
    passo = models.IntegerField()
    proxima_linha = models.IntegerField(default=-1)
    memoria_str = models.TextField(blank=True)
    terminal_str = models.TextField(blank=True)

    @property
    def memoria(self):
        return json.loads(self.memoria_str)

    @memoria.setter
    def memoria(self, mem):
        self.memoria_str = json.dumps(mem)

    @property
    def terminal(self):
        return json.loads(self.terminal_str)

    @terminal.setter
    def terminal(self, term):
        self.terminal_str = json.dumps(term)


class InteracaoUsuarioPassoTesteDeMesa(models.Model):
    interacao = models.ForeignKey(InteracaoUsarioExercicio,
                                  on_delete=models.CASCADE)
    passo = models.IntegerField()
    tentativas = models.IntegerField(default=0)
    melhor_resultado = models.CharField(max_length=2,
                                        choices=Resultado.choices,
                                        default=Resultado.ERRO)
    ultima_submissao = models.ForeignKey(RespostaSubmetida,
                                         on_delete=models.SET_NULL,
                                         blank=True,
                                         null=True)

    class Meta:
        unique_together = (
            'interacao',
            'passo',
        )

    objects = InteracaoUsuarioPassoTesteDeMesaManager()

    def __str__(self):
        return '{0}-{1}-{2} ({3}) [{4}]'.format(self.interacao.usuario,
                                                self.interacao.exercicio,
                                                self.passo, self.tentativas,
                                                self.melhor_resultado)
