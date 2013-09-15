from django.contrib.auth.models import Group

from .models import OneClickLinkToken

from datetime import datetime


def create_group(user_list):
    group = Group.objects.create(name=datetime.now())
    for user in user_list:
        user.groups.add(group)
    return group


def verify_ocl_token(token):
    try:
        ocl_token = OneClickLinkToken.objects.get(token=token)
    except OneClickLinkToken.DoesNotExist:
        return False
    return ocl_token