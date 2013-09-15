from django.contrib.auth import decorators
from django.conf import settings
from django.shortcuts import render, redirect
from cc.apps.accounts.models import OneClickLinkToken


def login_or_token_required(f, redirect_field_name='/'):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return f(request, *args, **kwargs)
        else:
            token = request.GET.get('token')
            if token:
                try:
                    ocl_token = OneClickLinkToken.objects.get(token=token)
                except OneClickLinkToken.DoesNotExist:
                    return redirect(settings.LOGIN_REDIRECT_URL)

                if ocl_token.expired:
                    return render(
                        request,
                        'registration/login.html',
                        {"ocl_expired": True}
                    )
                return f(request, *args, **kwargs)
            else:
                return redirect(settings.LOGIN_REDIRECT_URL)

    return wrap

is_superadmin = decorators.user_passes_test(
    lambda u: u.is_authenticated() and u.get_profile().is_superadmin)

is_admin = decorators.user_passes_test(
    lambda u: u.is_authenticated() and u.get_profile().is_admin)

is_user = decorators.user_passes_test(
    lambda u: u.is_authenticated() and u.get_profile().is_user)

is_not_sales_plus = decorators.user_passes_test(
    lambda u: u.is_authenticated() and not u.get_profilen().is_user_plus
)
