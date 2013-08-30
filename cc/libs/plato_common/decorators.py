# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@gmail.com>
#

"""View decorators common to apps in the Plato project.
"""


from django import http
from django.contrib.auth import decorators
from django.conf import settings
from django.shortcuts import render
from cc.apps.management.models import OneClickLinkToken


def _is_admin_or_superadmin(user):
    """Tests if user is an admin or a superadmin.

    This is a test function for the user_passes_test decorator. It also tests
    if user is authenticated, so you can skip @is_authenticated decorator on
    views.

    :return: True if user is an admin or a superadmin, otherwise returns False.
    """

    if not user.is_authenticated():
        return False

    profile = user.get_profile()
    return profile.is_admin or profile.is_superadmin

def login_or_token_required(f, redirect_field_name='/'):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return f(request, *args, **kwargs)
        else:
            token = request.GET.get('token')
            if token:
                try:
                    one_click_link_token = OneClickLinkToken.objects.get(token=token)
                except OneClickLinkToken.DoesNotExist, e:
                    return http.HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
                
                if one_click_link_token.expired:
                    return render(request,
                            'registration/login.html', {"ocl_expired": True})
                return f(request, *args, **kwargs)
            else:
                return http.HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    return wrap

is_admin_or_superadmin = decorators.user_passes_test(_is_admin_or_superadmin)

is_superadmin = decorators.user_passes_test(
    lambda u: u.is_authenticated() and u.get_profile().is_superadmin)

is_admin = decorators.user_passes_test(
    lambda u: u.is_authenticated() and u.get_profile().is_admin)

is_user = decorators.user_passes_test(
    lambda u: u.is_authenticated() and u.get_profile().is_user)

is_not_sales_plus = decorators.user_passes_test(
    lambda u: u.is_authenticated() and not u.get_profilen().is_user_plus
)


# vim: set et sw=4 ts=4 sts=4 tw=78:
