from collections import namedtuple
from django.db import models
import json

from .validators import json_validator
from core.models import Exercicio


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
    def gabarito_list(self):
        return [TraceData(*i) for i in json.loads(self.gabarito)]
