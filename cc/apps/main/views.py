from django.contrib.auth import decorators as auth_decorators

from cc.apps.reports.services import get_call_list

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/dashboard.html')
def dashboard(request):
    call_list = get_call_list(request.user)
    return {
        'call_list': call_list
    }
