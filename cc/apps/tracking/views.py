from django import http
from django.conf import settings
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session

from .models import TrackingEvent
from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message
from cc.apps.cc_messages.services import notify_email_opened

from annoying.decorators import ajax_request
from os import path


@csrf_exempt
@http_decorators.require_POST
@ajax_request
def create_event(request):
    '''
    Handles event creation
    '''
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')

    if message_id and user_id:
        addr_list = request.META.get('HTTP_X_FORWARDED_FOR')
        if addr_list:
            client_ip = addr_list.split(',')[-1].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR', None)

        event = TrackingEvent.objects.create(
            message=Message.objects.get(pk=message_id),
            participant=CUser.objects.get(pk=user_id),
            session=Session.objects.get(pk=request.session.session_key),
            event_type=TrackingEvent.OPEN_EVENT_TYPE,
            client_ip=client_ip
        )

        if event:
            return {'status': event.id}
        else:
            return {'status': 'ERROR'}
    else:
        return {'status': 'ERROR'}


def track_email(request, message_id, user_id):
    '''
    The 1x1 transparent image to track opened email
    '''
    # send email notification to owner of the message
    notify_email_opened(message_id, user_id)

    # serve the 1x1 transparent image
    img_abs_path = path.abspath(path.join(
        settings.STATICFILES_DIRS[0], 'img', 'transparent.gif'
    ))
    image_data = open(img_abs_path, 'rb').read()
    return http.HttpResponse(image_data, mimetype='image/gif')
