from django import template

register = template.Library()


@register.inclusion_tag('challenges/author.html')
def student_author(nome, turma, contribuicoes, foto=''):
    foto = 'assets/img/authors/' + foto
    return {'student': True, 'nome': nome, 'turma': turma, 'contribuicoes': contribuicoes, 'foto': foto}


@register.inclusion_tag('challenges/author.html')
def professor_author(nome, foto, contribuicoes):
    foto = 'assets/img/authors/' + foto
    return {'student': False, 'nome': nome, 'contribuicoes': contribuicoes, 'foto': foto}