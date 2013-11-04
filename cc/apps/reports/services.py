from cc.apps.accounts.models import CUser
from cc.apps.cc_messages.models import Message


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