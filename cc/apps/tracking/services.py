from .models import *
from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message


def validate_request(request):
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')
    request_type = request.POST.get('type')
    timer = request.POST.get('timer[1]')
    session_id = request.POST.get('session_id')

    if request_type == 'SESSION' and message_id and user_id:
        try:
            message = Message.objects.get(pk=message_id)
            user = CUser.objects.get(pk=user_id)
        except Message.DoesNotExist, CUser.DoesNotExist:
            return False
        return {'message': message, 'user': user}
    elif request_type == 'EVENT' and timer and int(session_id) > 0:
        return {'session_id': session_id}
    else:
        return False


def create_tracking_session(**kw):
    return TrackingSession.objects.create(
        message=kw['message'],
        participant=kw['user'],
        client_ip=kw['client_ip']
    )


def create_tracking_events_from_timer(session_id, timer_params):
    try:
        session = TrackingSession.objects.get(pk=session_id)
    except TrackingSession.DoesNotExist:
        print 'Invalid session'
        return False

    events = []
    for t in timer_params:
        page_number = t[0].replace('timer[', '').replace(']', '')
        events.append(TrackingEvent(
            tracking_session=session,
            page_number=page_number,
            total_time=t[1]
        ))

    return TrackingEvent.objects.bulk_create(events)
