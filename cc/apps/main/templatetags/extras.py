from django import template
from django.core.urlresolvers import reverse
from django.conf import settings


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
def settings_value(name):
    return getattr(settings, name, '')
