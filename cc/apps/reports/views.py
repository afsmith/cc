from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators import http as http_decorators
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import (
    get_tracking_data_group_by_recipient, get_missing_data,
    validate_request, get_tracking_data_group_by_page_number,
    get_recipient_without_tracking_data
)
from .models import Bounce
from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import TrackingSession
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
    tracking_data = get_tracking_data_group_by_recipient(this_message)

    # get missing data
    missing_data = get_missing_data(this_message)

    # get recipient without tracking data
    missing_recipients = get_recipient_without_tracking_data(this_message)

    return {
        'this_message': this_message,
        'messages': all_messages,
        'log_groupby_user': tracking_data,
        'missing_data': missing_data,
        'missing_recipients': missing_recipients
    }


@auth_decorators.login_required
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
            .order_by('created_at')
        )
        for qs in log_groupby_session:
            qs['created_ts'] = qs['created_at'].strftime('%d.%m.%Y %H:%M:%S')
            qs['total_time'] = format_dbtime(qs['total_time'])
        json_resp = json.dumps(
            list(log_groupby_session), cls=DjangoJSONEncoder
        )
        return HttpResponse(json_resp, mimetype='application/json')
    else:
        return {
            'status': 'ERROR',
            'message': 'Invalid arguments'
        }


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def report_drilldown(request):
    session_id = request.POST.get('session_id')
    recipient_id = request.POST.get('recipient_id')
    message_id = request.POST.get('message_id')

    this_message = get_object_or_404(Message, pk=message_id)

    if session_id:  # get session log
        data = get_tracking_data_group_by_page_number(
            tracking_session=session_id
        )
    elif recipient_id:  # get recipient log
        data = get_tracking_data_group_by_page_number(
            tracking_session__participant=recipient_id,
            tracking_session__message=message_id
        )
    else:  # get summary log
        data = get_tracking_data_group_by_page_number(
            tracking_session__message=message_id
        )

    return _format_data_for_chart(data, this_message)


def _format_data_for_chart(log, this_message):
    values = []
    labels = []
    combo = []
    for idx, p in enumerate(list(log)):
        values.append([idx, p[1]/10.0])
        labels.append([idx, 'Page {}'.format(p[0])])
        combo.append(['Page {}'.format(p[0]), p[1]/10.0])
    return {
        'values': values,
        'labels': labels,
        'combo': combo,
        'key_page': this_message.key_page,
        'subject': this_message.subject,
        'total_visits': log[0][2] if len(log) > 0 else 0
    }


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def remove_bounce(request, bounce_id):
    Bounce.objects.filter(pk=bounce_id).delete()
    return {}
