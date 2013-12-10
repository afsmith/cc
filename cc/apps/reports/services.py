from django.db.models import Sum, Count, Max

from . import algorithm

from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message
from cc.apps.tracking.models import TrackingSession, TrackingEvent, ClosedDeal

from cc.libs.utils import format_dbtime, get_hours_until_now


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


def get_completion_percentage(recipient_id, message):
    percent = 0
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
            #print percent, point_completion, point_visit, hours_last_visit, point_hours

            total_point = point_completion + point_visit + point_hours
            status_color = algorithm.get_status_color(total_point)
            #print total_point, status_color

            call_list.append({
                'total_point': total_point,
                'closed_deal': row['closed_deal'],
                'status': status_color,
                'date': row['max_date'],
                'email': row['tracking_session__participant__email'],
                'subject': message.subject,
            })
    
    # sort the call_list based on total_point
    call_list = sorted(call_list, key=lambda k: k['total_point']) 
    return call_list
