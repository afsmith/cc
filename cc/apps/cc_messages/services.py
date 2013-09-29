from django.conf import settings
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Message
from cc.apps.accounts.models import OneClickLinkToken, CUser

import datetime


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


def create_ocl_and_send_message(message, domain):
    '''
    Create OCL link (to the message) for each recipients and send email to them
    '''
    connection = get_connection()
    connection.open()
    recipient_emails = []

    for r in message.receivers.all():
        # ocl token should expire after 30 days
        ocl = OneClickLinkToken.objects.create(
            user=r,
            expires_on=datetime.datetime.today() + datetime.timedelta(days=30)
        )
        ocl_link = '%s/view/%d/?token=%s' % (
            domain, message.id, ocl.token
        )

        text_body = settings.EMAIL_TEMPLATE % {
            'message': message.message, 'ocl_link': ocl_link
        }
        msg = EmailMultiAlternatives(
            subject=message.subject,
            body=text_body,
            from_email=message.owner.email,
            to=[r.email],
            connection=connection
        )

        # attach the tracking pixel if needed
        if message.notify_email_opened:
            msg.attach_alternative(
                '%s <img src="%s/track/%d/%d" />' % (
                    text_body, domain, message.id, r.id
                ),
                'text/html'
            )
        msg.send()

        # add recipient email address to the list
        recipient_emails.append(r.email)

    # send a copy if sender chooses to cc himself
    if message.cc_me:
        msg = EmailMultiAlternatives(
            subject=message.subject,
            body=settings.CC_ME_TEMPLATE % {
                'recipients': ', '.join(recipient_emails),
                'message': message.message
            },
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[message.owner.email],
            connection=connection
        )
        msg.send()

    # close connection after finish
    connection.close()


def send_notification_email(reason_code, message, recipient=None):
    '''
    Send notification email to sender
    reason_code 1: email is opened
    reason_code 2: link is clicked
    reason_code 3: conversion error
    '''
    if reason_code == 1:
        subject = _('[Notification] %s opened your email.') % recipient.email
        email_template = settings.NOTIFICATION_EMAIL_OPENED_TEMPLATE
    elif reason_code == 2:
        subject = _('[Notification] %s clicked on your link.') % recipient.email
        email_template = settings.NOTIFICATION_LINK_CLICKED_TEMPLATE
    elif reason_code == 3:
        subject = _('[Notification] Conversion error.')
        email_template = settings.NOTIFICATION_CONVERSION_ERROR_TEMPLATE
    else:
        return None

    body = email_template % {
        'recipient': getattr(recipient, 'email', None),
        'subject': message.subject
    }

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[message.owner.email]
    )


def notify_email_opened(message_id, user_id):
    if message_id > 0 and user_id > 0:
        qs = Message.objects.filter(id=message_id, message__receivers=user_id)
        if qs:
            message = qs[0]
            if message.notify_email_opened:
                recipient = CUser.objects.get(id=user_id)
                # if all pass, send notification
                send_notification_email(1, message, recipient)
        else:
            return False
    else:
        return False
