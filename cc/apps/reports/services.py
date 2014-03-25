from django.db.models import Sum, Count, Max

from . import algorithm
from .models import Bounce

from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import (
    TrackingSession, TrackingEvent, ClosedDeal, TrackingLog
)

from cc.libs.utils import format_dbtime, get_hours_until_now

from datetime import datetime
from itertools import chain
import operator


def validate_request(request):
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')

    if message_id and user_id:
        try:
            message = Message.objects.get(pk=message_id)
            user = CUser.objects.get(pk=user_id)
        except Message.DoesNotExist, CUser.DoesNotExist:
            return False
        return {'message': message, 'user': user}
    else:
        return False


def get_tracking_data_group_by_recipient(message):
    tracking_data = (
        TrackingEvent.objects
        .filter(tracking_session__message=message)
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

    for row in tracking_data:
        # check if there is closed deal exists
        row['closed_deal'] = ClosedDeal.objects.filter(
            message=message,
            participant=row['tracking_session__participant']
        ).exists()
        # calculate the actual visit count (the above is 1 per page)
        row['visit_count'] /= message.files.all()[0].pages_num
        # format time
        row['total_time'] = format_dbtime(row['total_time'])

    return tracking_data


def get_missing_data(message):
    missing_data = chain(
        TrackingSession.objects
        .filter(message=message, trackingevent=None),

        TrackingLog.objects
        .exclude(trackingsession=1)
        .filter(
            message=message,
            action=TrackingLog.CLICK_LINK_ACTION,
            trackingsession=None
        )
    )

    return sorted(missing_data, key=operator.attrgetter('created_at'))


def get_tracking_data_group_by_page_number(**kwargs):
    tracking_data = (
        TrackingEvent.objects
        .filter(**kwargs)
        .values('page_number')
        .annotate(total_time=Sum('total_time'), total_visits=Count('id'))
        .order_by('page_number')
        .values_list('page_number', 'total_time', 'total_visits')
    )

    return tracking_data


def get_completion_percentage(recipient_id, message):
    tracking_data = (
        TrackingEvent.objects
        .filter(
            tracking_session__participant=recipient_id,
            tracking_session__message=message,
            total_time__gt=0
        )
        .aggregate(
            viewed_pages=Count('page_number', distinct=True),
        )
    )
    total_pages = message.files.all()[0].pages_num or 1

    return (tracking_data['viewed_pages'] / float(total_pages)) * 100


def get_call_list(user):
    call_list = []
    messages = Message.objects.filter(owner=user)
    for message in messages:
        # get tracking data
        tracking_data = get_tracking_data_group_by_recipient(message)
        for row in tracking_data:
            percent = get_completion_percentage(
                row['tracking_session__participant'],
                message
            )
            point_completion = algorithm.calculate_point(1, percent)
            point_visit = algorithm.calculate_point(2, row['visit_count'])
            hours_last_visit = get_hours_until_now(row['max_date'])
            point_hours = algorithm.calculate_point(3, hours_last_visit)

            total_point = point_completion + point_visit + point_hours
            status_color = algorithm.get_status_color(total_point)

            # add a row to call list
            call_list.append({
                'total_point': total_point,
                'closed_deal': row['closed_deal'],
                'status': status_color,
                'email': row['tracking_session__participant__email'],
                'date': message.created_at,
                'subject': message.subject,
                'recipient_id': row['tracking_session__participant'],
                'message_id': message.id,
            })

        # get list of people didn't look at the offer
        uninterested_recipients = CUser.objects.filter(
            receivers=message,
            trackingsession__isnull=True
        )
        for rec in uninterested_recipients:
            # add a row to call list
            call_list.append({
                'total_point': 0,
                'closed_deal': False,
                'status': algorithm.get_status_color(0),
                'email': rec.email,
                'date': message.created_at,
                'subject': message.subject,
                'recipient_id': rec.id,
                'message_id': message.id,
            })

    # sort the call_list based on total_point
    call_list = sorted(call_list, key=lambda k: k['total_point'], reverse=True)
    return call_list


def get_message_sent(user, period):
    now = datetime.now()
    if period == 'month':
        m = Message.objects.filter(owner=user, created_at__month=now.month)
        return m.count()


def save_sendgrid_bounce_from_request(json_request):
    # http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
    '''
    Example request
    [{u'status': u'5.1.1', u'smtp-id': u'<20140112225528.93299.71634@HMacPro.local>', u'sg_event_id': u'BJ7ASXa6RfOSV8Am2ydBiA', u'timestamp': 1389567336, u'domain': u'http://localhost:8000', u'event': u'bounce', u'reason': u"550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient's email address for typos or unnecessary spaces. Learn more at http://support.google.com/mail/bin/answer.py?answer=6596 ds9si14897314obc.21 - gsmtp ", u'cc_message_id': 40, u'type': u'bounce', u'email': u'hieu12347586q33@gmail.com'}]
    '''
    for req in json_request:
        event_type = req.get('event')
        # domain = req.get('domain')
        # smtp_id = req.get('smtp-id')
        cc_message_id = req.get('cc_message_id')
        email = req.get('email')
        reason = req.get('reason')

        if event_type in ['bounce', 'dropped']:
            msg = Message.objects.get(pk=cc_message_id)
            return Bounce.objects.create(
                email=email,
                reason=reason,
                message=msg,
                event_type=event_type
            )


def get_bounce_list(user):
    return Bounce.objects.filter(message__owner=user)
