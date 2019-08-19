from django import template

register = template.Library()

@register.filter
def get_css_class(submissions_by_challenge):
    try:
        if submissions_by_challenge.best_result == 'OK':
            return 'success'
        elif submissions_by_challenge.best_result == 'Erro' and submissions_by_challenge.attempts > 0:
            return 'error'
    except:
        pass
    return 'noattempt'

@register.filter
def get_css_count_class(count):
    if count > 0:
        return 'success'
    return 'noattempt'
