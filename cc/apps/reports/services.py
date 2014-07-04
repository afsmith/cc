from django.db.models import Sum, Count, Max
from django.core.exceptions import PermissionDenied

from . import algorithm
from .models import Bounce

from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import (
    TrackingSession, TrackingEvent, ClosedDeal, TrackingLog
)

from cc.libs.utils import format_dbtime, get_hours_until_now

from datetime import datetime, timedelta
from itertools import chain
import operator


def validate_request(request):
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')
    file_index = request.POST.get('file_index')

    if message_id and user_id:
        try:
            message = Message.objects.get(pk=message_id)
            user = CUser.objects.get(pk=user_id)
        except Message.DoesNotExist, CUser.DoesNotExist:
            return False
        return {'message': message, 'user': user, 'file_index': file_index}
    else:
        return False


def check_permission(message, user):
    if message.owner != user:
        raise PermissionDenied


def get_tracking_data_group_by_recipient(message, file_index=None):
    qs = TrackingEvent.objects.filter(
        tracking_session__message=message
    ).values(
        'tracking_session__participant',
        'tracking_session__participant__email',
    )
    # if there is file_index, query per file
    if file_index:
        qs = TrackingEvent.objects.filter(
            tracking_session__message=message,
            tracking_session__file_index=file_index
        ).values(
            'tracking_session__participant',
            'tracking_session__participant__email',
            'tracking_session__file_index',
        )

    tracking_data = qs.annotate(
        total_time=Sum('total_time'),
        ip_count=Count('tracking_session__client_ip', distinct=True),
        device_count=Count('tracking_session__device', distinct=True),
        visit_count=Count('id'),
        last_visit=Max('tracking_session__created_at'),
    ).order_by()

    for row in tracking_data:
        # check if there is closed deal exists
        row['closed_deal'] = ClosedDeal.objects.filter(
            message=message,
            participant=row['tracking_session__participant']
        ).exists()
        # calculate the actual visit count (the above is 1 per page)
        if file_index:
            row['visit_count'] /= message.files.get(index=file_index).pages_num
        else:
            row['visit_count'] /= get_total_pages(message)
        # format time
        row['total_time'] = format_dbtime(row['total_time'])

    return tracking_data


def get_recipients_without_tracking_data(message, session_only=True):
    qs = CUser.objects.filter(
        receivers=message
    ).exclude(
        trackingsession__message=message
    )
    if session_only:
        return qs
    else:
        return qs.exclude(trackinglog__message=message)


def get_missing_data(message):
    missing_data = chain(
        TrackingSession.objects
        .filter(message=message, trackingevent=None),

        TrackingLog.objects
        .filter(
            message=message,
            action=TrackingLog.CLICK_LINK_ACTION,
            revision__gt=1,
            trackingsession=None,
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


def get_email_action_group_by_recipient(message, recipient=None):
    qs = TrackingLog.objects.filter(
        message=message,
        action=TrackingLog.OPEN_EMAIL_ACTION
    )
    if recipient:
        qs = qs.filter(participant=recipient)

    return qs.values(
        'participant',
        'participant__email'
    ).annotate(
        visit_count=Count('id'),
        last_visit=Max('created_at'),
    ).order_by()


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
    total_pages = get_total_pages(message)

    return (tracking_data['viewed_pages'] / float(total_pages)) * 100


def get_total_pages(message):
    return sum([
        f.pages_num if f.pages_num else 1 for f in message.files.all()
    ])


def get_call_list(user, past_days=14):
    call_list = []
    messages = Message.objects.filter(
        owner=user,
        created_at__gte=datetime.today()-timedelta(days=past_days)
    )
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
            point_hours = algorithm.calculate_point(
                3, get_hours_until_now(row['last_visit'])
            )

            total_point = point_completion + point_visit + point_hours
            status_color = algorithm.get_status_color(total_point)

            # add a row to call list
            call_list.append({
                'total_point': total_point,
                'attachment': message.files.count(),
                'status': status_color,
                'email': row['tracking_session__participant__email'],
                'recipient_id': row['tracking_session__participant'],
                'message': message,
            })

        # get list of people that don't have tracking session
        no_session = get_recipients_without_tracking_data(message)
        for recipient in no_session:
            # if this message doesn't have any attachment
            if message.files.count() == 0:
                total_point = 0
                tracking_data = get_email_action_group_by_recipient(
                    message, recipient
                )
                # calculate points for this recipient
                if tracking_data:
                    point_visit = algorithm.calculate_point(
                        2, tracking_data[0]['visit_count']
                    )
                    point_hours = algorithm.calculate_point(
                        3, get_hours_until_now(
                            tracking_data[0]['last_visit']
                        )
                    )
                    point_completion = algorithm.calculate_point(4, True)
                    total_point = point_completion + point_visit + point_hours

                call_list.append({
                    'total_point': total_point,
                    'attachment': message.files.count(),
                    'status': algorithm.get_status_color(total_point),
                    'email': recipient.email,
                    'recipient_id': recipient.id,
                    'message': message,
                })
            else:
                # recipient doesn't look at offer
                call_list.append({
                    'total_point': 0,
                    'attachment': message.files.count(),
                    'status': algorithm.get_status_color(0),
                    'email': recipient.email,
                    'recipient_id': recipient.id,
                    'message': message,
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


def get_last_email_open(message, recipient=None):
    qs = TrackingLog.objects.filter(
        message=message, action=TrackingLog.OPEN_EMAIL_ACTION
    )
    if recipient:
        qs.filter(participant=recipient)

    return qs.order_by('-created_at')[0]


def get_messages_with_email_data(user, past_days=7):
    rows = []

    # get all messages from recent days
    messages = Message.objects.filter(
        owner=user,
        created_at__gte=datetime.today()-timedelta(days=past_days)
    ).order_by('-created_at')

    for message in messages:
        # check if there is any open action from message
        logs = (
            TrackingLog.objects
            .filter(message=message, action=TrackingLog.OPEN_EMAIL_ACTION)
            .values('message')
            .annotate(
                visit_count=Count('id'),
                last_visit=Max('created_at'),
            )
        )

        if logs:
            # get the log of last open
            last_log = get_last_email_open(message)
            rows.append({
                'message': message,
                'visit_count': logs[0]['visit_count'],
                'last_visit': logs[0]['last_visit'],
                'device': last_log.device,
                'location': last_log.location,
                'resend': False,
            })
        else:
            rows.append({
                'message': message,
                'visit_count': 0,
                'resend': True,
            })

    return rows


def get_tracking_data_group_by_link(message_id):
    log = (
        TrackingLog.objects
        .filter(message=message_id, action=TrackingLog.CLICK_EXT_LINK_ACTION)
        .values('link__original_url')
        .annotate(
            count=Count('id'),
        )
    )

    return log
