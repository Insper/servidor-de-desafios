from django import template
from core.choices import Resultado

register = template.Library()


@register.filter
def get_css_class(submissoes_por_exercicio):
    try:
        if submissoes_por_exercicio.melhor_resultado == Resultado.OK:
            return 'success'
        elif submissoes_por_exercicio.melhor_resultado == Resultado.ERRO and submissoes_por_exercicio.tentativas > 0:
            return 'error'
    except:
        pass
    return 'noattempt'


@register.filter
def get_css_count_class(count):
    if count > 0:
        return 'success'
    return 'noattempt'
