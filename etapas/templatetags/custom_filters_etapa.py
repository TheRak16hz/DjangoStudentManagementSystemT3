from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))


@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, None)