from .models import *
from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message


def validate_request(request):
    message_id = request.POST.get('message_id')
    user_id = request.POST.get('user_id')
    request_type = request.POST.get('type')
    timer = request.POST.get('timer[1]')

    if request_type == 'SESSION' and message_id and user_id:
        try:
            message = Message.objects.get(pk=message_id)
            user = CUser.objects.get(pk=user_id)
        except Message.DoesNotExist, CUser.DoesNotExist:
            return False
        return {'message': message, 'user': user}
    elif request_type == 'EVENT' and timer:
        return True
    else:
        return False


def create_tracking_session(**kw):
    return TrackingSession.objects.create(
        message=kw['message'],
        participant=kw['user'],
        client_ip=kw['client_ip']
    )
