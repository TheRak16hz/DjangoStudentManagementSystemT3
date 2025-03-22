from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Devuelve el valor de un diccionario dado un key."""
    return dictionary.get(key)

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, None)