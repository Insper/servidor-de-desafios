from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(key)
    return None

@register.filter
def get_css_class(submissions_by_challenge):
    if submissions_by_challenge.best_result == 'OK':
        return 'success'
    elif submissions_by_challenge.best_result == 'Erro' and len(submissions_by_challenge.submissions) > 0:
        return 'error'
    return 'noattempt'

@register.filter
def get_css_count_class(count):
    if count > 0:
        return 'success'
    return 'noattempt'