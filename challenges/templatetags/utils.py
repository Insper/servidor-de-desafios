from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(key)
    return None

@register.filter
def smartname(user):
    name = ''
    if user.first_name:
        name = user.first_name.capitalize()
    if user.last_name:
        name += ' {0}'.format(user.last_name.split()[-1].capitalize())
    if not name:
        name = user.username
    return name.strip()
