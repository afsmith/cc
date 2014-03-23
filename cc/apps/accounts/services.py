from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from .models import OneClickLinkToken, Invitation

from templated_email import send_templated_mail
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
    if ocl_token.expired:
        return False
    return ocl_token


def send_invitation_email(invitation, domain):
    if invitation.status == Invitation.STATUS_SENT:
        link = '{}{}?invitation_code={}'.format(
            domain, reverse('accounts_register'), invitation.code
        )

        send_templated_mail(
            template_name='invitation',
            from_email=invitation.from_user.email,
            recipient_list=[invitation.to_email],
            context={
                'link': link,
            }
        )
    elif invitation.status == Invitation.STATUS_ACCEPTED:
        send_templated_mail(
            template_name='invitation_active',
            from_email=invitation.from_user.email,
            recipient_list=[invitation.to_email],
            context={}
        )
