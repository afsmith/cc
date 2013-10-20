from django import template
from django.core.urlresolvers import reverse

register = template.Library()
@register.filter('type')
def type(obj):
    return obj.__class__.__name__


@register.simple_tag
def active(request, route):
    if request.path == reverse(route):
        return 'active'
    return ''


@register.simple_tag
def to_second(number):
    if number is None:
        return 0
    return (number / 100)
