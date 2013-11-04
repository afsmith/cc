from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum, Count, Max
from django.http import HttpResponse
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

from .services import validate_request
from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import TrackingSession, TrackingEvent


from annoying.decorators import render_to, ajax_request
import json


@auth_decorators.login_required
@render_to('main/dashboard.html')
def dashboard(request):
    return {}


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

    log_groupby_user = (
        TrackingEvent.objects
        .filter(tracking_session__message=message_id)
        .values(
            'tracking_session__participant',
            'tracking_session__participant__email'
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
    #print log_groupby_user.query.__str__()

    if request.is_ajax():
        log_groupby_page_number = (
            TrackingEvent.objects
            .filter(tracking_session__message=message_id)
            .values('page_number')
            .annotate(total_time=Sum('total_time'))
            .order_by('page_number')
            .values_list('page_number', 'total_time')
        )
        # format the data nicely
        formatted_data = []
        for p in list(log_groupby_page_number):
            row = ['Page {}'.format(p[0]), p[1]/100.0]
            if this_message.key_page and this_message.key_page == p[0]:
                row.append('Key page: {}s'.format(p[1]/100.0))
            else:
                row.append('{}s'.format(p[1]/100.0))
            formatted_data.append(row)
        # and return to JS via json
        json_resp = json.dumps(formatted_data)
        return HttpResponse(json_resp, mimetype='application/json')
    else:
        return {
            'this_message': this_message,
            'messages': all_messages,
            'log_groupby_user': log_groupby_user
        }


@csrf_exempt
@http_decorators.require_POST
@ajax_request
def user_log(request):
    data = validate_request(request)
    if data:
        log_groupby_session = (
            TrackingSession.objects
            .filter(message=data['message'], participant=data['user'])
            .extra(select={
                'total_time': """SELECT SUM(total_time) 
                    FROM tracking_trackingevent 
                    WHERE tracking_trackingevent.tracking_session_id 
                        = tracking_trackingsession.id"""
            })
            .values('created_at', 'total_time', 'client_ip', 'device')
        )
        json_resp = json.dumps(list(log_groupby_session), cls=DjangoJSONEncoder)
        return HttpResponse(json_resp, mimetype='application/json')
    else:
        return {
            'status': 'ERROR',
            'message': 'Invalid arguments'
        }
