from django import template

register = template.Library()
@register.filter('type')
def type(obj):
    return obj.__class__.__name__
