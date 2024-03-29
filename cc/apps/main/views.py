from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from django.conf import settings

from cc.apps.accounts.models import CUser
from cc.apps.reports import services
from cc.libs.utils import get_domain


from annoying.decorators import render_to
import json


@ensure_csrf_cookie
@auth_decorators.login_required
@render_to('main/dashboard.html')
def dashboard(request):
    message_sent = services.get_message_sent(request.user, 'month')
    call_list = services.get_call_list(request.user)
    bounce_list = services.get_bounce_list(request.user)
    message_list = services.get_messages_with_email_data(request.user)

    return {
        'call_list': call_list,
        'message_sent': message_sent,
        'message_list': message_list,
        'bounce_list': bounce_list,
    }


@csrf_exempt
def sendgrid_parse(request):
    if request.body:
        try:
            json_req = json.loads(request.body)
        except ValueError:
            # if request is not a JSON string, return status 200 and send email
            send_mail(
                'Sendgrid bounce report - non JSON',
                request.body,
                settings.DEFAULT_FROM_EMAIL,
                ['hieu@sudointeractive.com']
            )

            return HttpResponse(status=200)

        # filter the request
        if (
            isinstance(json_req, list) and len(json_req) > 0
            and json_req[0].get('smtp-id')
            and json_req[0].get('cc_message_id')
            and json_req[0].get('domain') == get_domain(request)
        ):
            services.save_sendgrid_bounce_from_request(json_req)
        elif settings.DEBUG:
            send_mail(
                'Sendgrid debug report',
                request.body,
                settings.DEFAULT_FROM_EMAIL,
                ['hieu@sudointeractive.com']
            )

    # response with status 200 no matter what
    return HttpResponse(status=200)


@auth_decorators.login_required
@render_to('main/profile.html')
def profile_view(request):
    user_profile = list(CUser.objects.all())
    return {
        'user_profile': user_profile,
    }
