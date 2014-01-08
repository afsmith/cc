from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import decorators as auth_decorators

from cc.apps.reports.services import *

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/dashboard.html')
def dashboard(request):
    message_sent = get_message_sent(request.user, 'month')
    call_list = get_call_list(request.user)
    bounce_list = get_bounce_list(request.user)

    return {
        'message_sent': message_sent,
        'call_list': call_list,
        'bounce_list': bounce_list,
    }


@csrf_exempt
def sendgrid_parse(request):
    if request.POST.get('headers') and request.POST.get('subject'):
        save_sendgrid_bounce_from_request(request.POST)

    # response with status 200 no matter what
    return HttpResponse(status=200)