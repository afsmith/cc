from django import http
from django.conf import settings
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import csrf_exempt

from .services import validate_request, create_tracking_session, create_tracking_events_from_timer
from cc.apps.cc_messages.services import notify_email_opened
from cc.libs.utils import get_client_ip

from annoying.decorators import ajax_request
from os import path


@csrf_exempt
@http_decorators.require_POST
@ajax_request
def create_event(request):
    '''
    Handles tracking event and session creation
    '''
    data = validate_request(request)
    if data:
        if request.POST['type'] == 'SESSION':
            session = create_tracking_session(
                message=data['message'],
                user=data['user'],
                session_key=request.session.session_key,
                client_ip=get_client_ip(request)
            )

            if session:
                return {
                    'status': 'OK',
                    'session': session.id
                }
        elif request.POST['type'] == 'EVENT':
            # since timer parameters are sent in format: timer[1], timer[2]
            # we need to get them into a list
            timer_params = [
                (x, request.POST.get(x)) 
                for x in request.POST if x.startswith('timer')
            ]
            print create_tracking_events_from_timer(data['session_id'], timer_params)

            return {}
    else:
        return {
            'status': 'ERROR',
            'message': 'Invalid arguments'
        }


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
