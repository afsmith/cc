from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from cc.apps.cc_messages.models import Message


def get_message(id, user):
    '''
    Get message if the user has permission to view it
    '''
    if id:
        message = get_object_or_404(Message, pk=id)
        if message.is_available_for_user(user):
            return message
        else:
            raise PermissionDenied
