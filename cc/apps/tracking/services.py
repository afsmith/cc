from .models import *
from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message

import re


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
        if action in ['create', 'remove'] and message_id and user_id:
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


def create_tracking_events(session_id, timer_params, counter_params):
    try:
        session = TrackingSession.objects.get(pk=session_id)
    except TrackingSession.DoesNotExist:
        print 'Invalid session'
        return False

    events = []
    for key in timer_params.keys():
        # timer_params format example: {'timer[0]': '100', 'timer[1]': '200'}
        page_number = int(re.search('\d+', key).group(0))
        
        param_str = timer_params.get(key)
        if param_str == 'NaN':
            param_str = '0'
        total_time = int(param_str)

        param_str = counter_params.get('counter[{}]'.format(page_number))
        if param_str == 'NaN':
            param_str = '0'
        page_view = int(param_str)
        
        events.append(TrackingEvent(
            tracking_session=session,
            page_number=page_number,
            total_time=total_time,
            page_view=page_view
        ))

    return TrackingEvent.objects.bulk_create(events)

def edit_or_create_tracking_events(
        session_id, timer_params, counter_params, is_replace=False
    ):
    events = TrackingEvent.objects.filter(tracking_session=session_id)
    if events:
        for event in events:
            current_page_time = int(
                timer_params.get('timer[{}]'.format(event.page_number))
            )
            current_page_count = int(
                counter_params.get('counter[{}]'.format(event.page_number))
            )

            # if this is Safari Desktop tracking event, the later data should
            # replace the previous one
            if is_replace:    
                event.total_time = current_page_time
                event.page_view = current_page_count
            # otherwise, just sum up the data (in 'pagehide' event)
            else:
                event.total_time += current_page_time
                event.page_view += current_page_count

            # save the event
            event.save()
    else:
        return create_tracking_events(session_id, timer_params, counter_params)


def create_closed_deal(**kw):
    return ClosedDeal.objects.create(
        message=kw['message'],
        participant=kw['user']
    )


def remove_closed_deal(**kw):
    return ClosedDeal.objects.filter(
        message=kw['message'],
        participant=kw['user']
    ).delete()
