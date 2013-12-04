from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum, Count, Max
from django.http import HttpResponse
from django.views.decorators import http as http_decorators
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import validate_request
from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import TrackingSession, TrackingEvent, ClosedDeal
from cc.libs.utils import format_dbtime

from annoying.decorators import render_to, ajax_request
import json


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


@ensure_csrf_cookie
@auth_decorators.login_required
@render_to('main/report_detail.html')
def report_detail(request, message_id):
    '''
    Reporting detail view
    '''
    this_message = get_object_or_404(Message, pk=message_id)

    # get all messages for dropdown
    all_messages = (
        Message.objects.filter(owner=request.user)
        .order_by('created_at').reverse()
    )

    # get log data group by participant
    log_groupby_user = (
        TrackingEvent.objects
        .filter(tracking_session__message=message_id)
        .values(
            'tracking_session__participant',
            'tracking_session__participant__email',
        )
        .annotate(
            total_time=Sum('total_time'),
            ip_count=Count('tracking_session__client_ip', distinct=True),
            device_count=Count('tracking_session__device', distinct=True),
            visit_count=Count('id'),
            max_date=Max('tracking_session__created_at'),
        )
        .order_by()
    )

    for qs in log_groupby_user:
        # check if there is closed deal exists
        qs['closed_deal'] = ClosedDeal.objects.filter(
            message=message_id,
            participant=qs['tracking_session__participant']
        ).exists()
        # calculate the actual visit count (the above is 1 per page)
        qs['visit_count'] /= this_message.files.all()[0].pages_num
        # format time
        qs['total_time'] = format_dbtime(qs['total_time'])
    
    #print log_groupby_user.query.__str__()
    
    return {
        'this_message': this_message,
        'messages': all_messages,
        'log_groupby_user': log_groupby_user
    }


@http_decorators.require_POST
@ajax_request
def summary_log(request):
    message_id = request.POST.get('message_id')
    this_message = get_object_or_404(Message, pk=message_id)

    log_groupby_page_number = (
        TrackingEvent.objects
        .filter(tracking_session__message=message_id)
        .values('page_number')
        .annotate(total_time=Sum('total_time'))
        .order_by('page_number')
        .values_list('page_number', 'total_time')
    )

    return _format_data_for_chart(log_groupby_page_number, this_message)


@http_decorators.require_POST
@ajax_request
def user_log(request):
    data = validate_request(request)
    if data:
        log_groupby_session = (
            TrackingSession.objects
            .filter(message=data['message'], participant=data['user'])
            .annotate(total_time=Sum('trackingevent__total_time'))
            .filter(total_time__gt=0)
            .values('id', 'created_at', 'total_time', 'client_ip', 'device')
        )
        for qs in log_groupby_session:
            qs['created_ts'] = qs['created_at'].strftime('%d.%m.%Y %H:%M:%S')
            qs['total_time'] = format_dbtime(qs['total_time'])
        json_resp = json.dumps(list(log_groupby_session), cls=DjangoJSONEncoder)
        return HttpResponse(json_resp, mimetype='application/json')
    else:
        return {
            'status': 'ERROR',
            'message': 'Invalid arguments'
        }


@http_decorators.require_POST
@ajax_request
def session_log(request):
    session_id = request.POST.get('session_id')
    message_id = request.POST.get('message_id')
    this_message = get_object_or_404(Message, pk=message_id)

    log_groupby_page_number = (
        TrackingEvent.objects
        .filter(tracking_session=session_id)
        .values('page_number')
        .annotate(total_time=Sum('total_time'))
        .order_by('page_number')
        .values_list('page_number', 'total_time')
    )
    return _format_data_for_chart(log_groupby_page_number, this_message)


def _format_data_for_chart(log, this_message):
    formatted_data = []
    for p in list(log):
        row = ['Page {}'.format(p[0]), p[1]/10.0]
        if this_message.key_page and this_message.key_page == p[0]:
            row.append('Key page: {}'.format(p[1]/10.0))
        else:
            row.append('{}'.format(p[1]/10.0))
        formatted_data.append(row)
    return formatted_data
