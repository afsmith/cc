from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum

from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import TrackingSession, TrackingEvent

from annoying.decorators import render_to


@auth_decorators.login_required
@render_to('main/report_index.html')
def report_index(request):
    '''
    Reporting main view
    '''
    try:
        latest_message = (
            Message.objects.filter(owner=request.user).latest('created_at')
        )
    except Message.DoesNotExist:
        return {}
    
    return redirect('report_detail', message_id=latest_message.id)


@auth_decorators.login_required
@render_to('main/report_detail.html')
def report_detail(request, message_id):
    '''
    Reporting detail view
    '''
    this_message = get_object_or_404(Message, pk=message_id)

    all_messages = (
        Message.objects.filter(owner=request.user)
        .order_by('created_at').reverse()
    )

    log = (
        TrackingSession.objects
        .filter(message=message_id)
        .extra(select={
            'total_time': "SELECT SUM(total_time) FROM tracking_trackingevent WHERE tracking_trackingevent.tracking_session_id = tracking_trackingsession.id"
        })
    )
    
    '''
    TrackingEvent.objects.filter(tracking_session__message=message_id).aggregate(Sum('total_time'))
    log2 = (
        TrackingEvent.objects
        .filter(tracking_session__message=message_id)
        .values('tracking_session')
        .annotate(total_time=Sum('total_time'))
    )
    '''

    return {
        'this_message': this_message,
        'messages': all_messages,
        'log': log,
    }