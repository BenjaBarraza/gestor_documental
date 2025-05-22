from django import template

register = template.Library()

@register.filter
def split_comas(value):
    return [e.strip() for e in value.split(',') if e.strip()]

@register.filter
def trim(value):
    return value.strip()