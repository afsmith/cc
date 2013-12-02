from django import http
from django.conf import settings
from django.views.decorators import http as http_decorators

from .services import *
from cc.apps.cc_messages.services import notify_email_opened
from cc.libs.utils import get_client_ip, get_device_name

from annoying.decorators import ajax_request
from os import path


@http_decorators.require_POST
@ajax_request
def create_event(request):
    '''
    Handles tracking event and session creation
    '''
    data = validate_request(request, 'event')
    if data:
        if request.POST['type'] == 'SESSION':
            session = create_tracking_session(
                message=data['message'],
                user=data['user'],
                client_ip=get_client_ip(request),
                device=get_device_name(request)
            )

            if session:
                return {
                    'status': 'OK',
                    'session_id': session.id,
                    'is_iOS': session.device in ['iPhone', 'iPad', 'iPod']
                }
            else:
                return {
                    'status': 'ERROR',
                    'message': session.__str__()
                }
        elif request.POST['type'] == 'EVENT':
            # since timer parameters are sent in format: timer[1], timer[2]
            # we need to get them into a dict and the same for counter
            timer_params = {}
            counter_params = {}
            for req in request.POST:
                if req.startswith('timer'):
                    timer_params[req] = request.POST.get(req)
                elif req.startswith('counter'):
                    counter_params[req] = request.POST.get(req)
            
            if request.POST['event_type'] == 'beforeunload':
                # save events in DB
                create_tracking_events(
                    data['session_id'], timer_params, counter_params
                )
            elif request.POST['event_type'] == 'pagehide':
                # do something about it

            # response doesn't do anything special so just send a blank one
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


@http_decorators.require_POST
@ajax_request
def close_deal(request):
    data = validate_request(request, 'deal')
    if data:
        if request.POST['action'] == 'create':
            # create closed deal
            closed_deal = create_closed_deal(
                message=data['message'],
                user=data['user']
            )
            if closed_deal:
                return {
                    'status': 'OK',
                    'closed_deal': closed_deal.id
                }
            else:
                return {
                    'status': 'ERROR',
                    'message': closed_deal.__str__()
                }
        else:
            # remove closed deal
            remove_closed_deal(
                message=data['message'],
                user=data['user']
            )
            return {
                'status': 'OK',
            }
    else:
        return {
            'status': 'ERROR',
            'message': 'Invalid arguments'
        }
