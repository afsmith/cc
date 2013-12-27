from django.contrib.auth import decorators as auth_decorators

from cc.apps.reports.services import get_call_list, get_message_sent

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/dashboard.html')
def dashboard(request):
    message_sent = get_message_sent(request.user, 'month')
    call_list = get_call_list(request.user)

    return {
        'message_sent': message_sent,
        'call_list': call_list
    }
