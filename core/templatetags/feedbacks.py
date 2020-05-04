from django import template

register = template.Library()

@register.inclusion_tag('core/feedbacks.html')
def show_feedbacks(respostas, error_counter):
    return {'respostas': respostas, 'error_counter': error_counter}
   
