from .models import *
from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message


def validate_request(request, type):
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')
    request_type = request.POST.get('type')
    timer = request.POST.get('timer[1]')
    session_id = request.POST.get('session_id')
    action = request.POST.get('action')

    if type == 'event':
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
    elif type == 'deal':
        if action and message_id and user_id:
            try:
                message = Message.objects.get(pk=message_id)
                user = CUser.objects.get(pk=user_id)
            except Message.DoesNotExist, CUser.DoesNotExist:
                return False
            return {'message': message, 'user': user}
        else:
            return False


def create_tracking_session(**kw):
    return TrackingSession.objects.create(
        message=kw['message'],
        participant=kw['user'],
        client_ip=kw['client_ip'],
        device=kw['device']
    )


def create_tracking_events_from_timer(session_id, timer_params):
    try:
        session = TrackingSession.objects.get(pk=session_id)
    except TrackingSession.DoesNotExist:
        print 'Invalid session'
        return False

    events = []
    for t in timer_params:
        page_number = int(t[0].replace('timer[', '').replace(']', ''))
        total_time = int(t[1])
        events.append(TrackingEvent(
            tracking_session=session,
            page_number=page_number,
            total_time=total_time
        ))

    return TrackingEvent.objects.bulk_create(events)


def create_closed_deal(**kw):
    return ClosedDeal.objects.create(
        message=kw['message'],
        participant=kw['user']
    )