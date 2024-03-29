from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators import http as http_decorators
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import ensure_csrf_cookie

from . import services
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
            Message.objects
            .filter(owner=request.user)
            .exclude(files=None)
            .latest('created_at')
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
    services.check_permission(this_message, request.user)

    # get all messages for dropdown
    all_messages = (
        Message.objects
        .filter(owner=request.user)
        .exclude(files=None)
        .order_by('created_at').reverse()
    )

    # get missing data
    missing_data = services.get_missing_data(this_message)

    # get recipient without tracking data
    uninterested_recipients = services.get_recipients_without_tracking_data(
        this_message, False
    )

    return {
        'this_message': this_message,
        'messages': all_messages,
        'missing_data': missing_data,
        'uninterested_recipients': uninterested_recipients
    }


@ensure_csrf_cookie
@auth_decorators.login_required
@render_to('main/_report_graph_table.html')
def report_detail_per_file(request, message_id, file_index):
    this_message = get_object_or_404(Message, pk=message_id)
    services.check_permission(this_message, request.user)

    # get log data group by participant
    tracking_data = services.get_tracking_data_group_by_recipient(
        this_message, file_index
    )
    # get the file
    f = this_message.files.get(index=file_index)

    return {
        'this_message': this_message,
        'tracking_data': tracking_data,
        'file': f
    }


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def user_log(request):
    data = services.validate_request(request)
    if data:
        log_groupby_session = (
            TrackingSession.objects
            .filter(
                message=data['message'],
                participant=data['user'],
                file_index=data['file_index'],
            )
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
    file_index = request.POST.get('file_index')

    this_message = get_object_or_404(Message, pk=message_id)
    services.check_permission(this_message, request.user)

    if session_id:  # get session log from report detail
        data = services.get_tracking_data_group_by_page_number(
            tracking_session=session_id
        )
    elif recipient_id:  # get recipient log from dashboard
        data = services.get_tracking_data_group_by_page_number(
            tracking_session__participant=recipient_id,
            tracking_session__message=message_id,
            tracking_session__file_index=file_index
        )
    else:  # get summary log from report detail
        data = services.get_tracking_data_group_by_page_number(
            tracking_session__message=message_id,
            tracking_session__file_index=file_index,
        )

    return _format_data_for_chart(data, this_message, file_index)


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def report_dashboard(request):
    recipient_id = request.POST.get('recipient_id')
    message_id = request.POST.get('message_id')
    file_index = request.POST.get('file_index')

    this_message = get_object_or_404(Message, pk=message_id)
    services.check_permission(this_message, request.user)

    if recipient_id and message_id and file_index:
        data = services.get_tracking_data_group_by_page_number(
            tracking_session__participant=recipient_id,
            tracking_session__message=message_id,
            tracking_session__file_index=file_index
        )
        formatted_data = _format_data_for_chart(data, this_message, file_index)

        return {
            'status': 'OK',
            #'files': files,
            'file_count': this_message.files.count(),
            'data': formatted_data
        }
    else:
        return {
            'status': 'ERROR'
        }


def _format_data_for_chart(data, this_message, file_index):
    values = []
    labels = []
    combo = []
    imgs = []
    limit = 10 * 60  # 10 minutes
    is_bigger_than_limit = False

    # get images for file
    f = this_message.files.get(index=file_index)

    # get tracking data
    for idx, p in enumerate(list(data)):
        values.append([idx, p[1]/10.0])
        labels.append([idx, 'Page {}'.format(p[0])])
        combo.append(['Page {}'.format(p[0]), p[1]/10.0])
        imgs.append('{}/{}.png'.format(f.view_url, (idx+1)))
        if p[1]/10.0 > limit:
            is_bigger_than_limit = True

    return {
        'values': values,
        'labels': labels,
        'combo': combo,
        'imgs': imgs,
        'subject': this_message.subject,
        'total_visits': data[0][2] if len(data) > 0 else 0,
        'is_bigger_than_limit': is_bigger_than_limit,
    }


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def remove_bounce(request, bounce_id):
    Bounce.objects.filter(pk=bounce_id).delete()
    return {}


@auth_decorators.login_required
@http_decorators.require_POST
@render_to('main/_dashboard_call_list_table.html')
def report_call_list(request):
    past_days = int(request.POST.get('days', '14'))
    call_list = services.get_call_list(request.user, past_days)

    return {'call_list': call_list}


@auth_decorators.login_required
@http_decorators.require_POST
@render_to('main/_dashboard_message_list_table.html')
def report_message_list(request):
    past_days = int(request.POST.get('days', '7'))
    message_list = services.get_messages_with_email_data(
        request.user, past_days
    )

    return {'message_list': message_list}


@auth_decorators.login_required
@http_decorators.require_POST
@render_to('main/_dashboard_right.html')
def report_email_opened(request):
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')
    log = services.get_email_action_group_by_recipient(
        message_id, user_id
    )
    if log and log[0]['visit_count'] > 0:
        last_open = services.get_last_email_open(message_id, user_id)
        return {
            'count': log[0]['visit_count'],
            'last_open': last_open
        }
    return {}


@auth_decorators.login_required
@http_decorators.require_POST
@render_to('main/_dashboard_external_link_table.html')
def report_external_links(request):
    message_id = request.POST.get('message_id')
    log = services.get_tracking_data_group_by_link(message_id)
    return {'log': log}
