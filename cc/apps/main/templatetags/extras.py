from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings

import re

register = template.Library()


@register.filter('type')
def type(obj):
    return obj.__class__.__name__


@register.simple_tag
def active(request, route):
    try:
        pattern = reverse(route)
    except NoReverseMatch:
        pattern = route
    path = request.path
    if path == pattern:
        return 'active'
    else:
        match = re.search(pattern, path)
        if match and match.group() != '/':
            return 'active'
    return ''


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, '')


@register.filter
def get_range(value):
    return range(value)


@register.filter
def is_in(value, list_str):
    return value in list_str.split(',')
