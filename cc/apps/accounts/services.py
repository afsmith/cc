from django.contrib.auth.models import Group

from datetime import datetime


def create_group(user_list):
    group = Group.objects.create(name=datetime.now())
    for user in user_list:
        user.groups.add(group)
    return group
