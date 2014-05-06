from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Message
from cc.apps.reports.models import Bounce
from cc.apps.accounts.models import OneClickLinkToken, CUser
from cc.apps.tracking.models import TrackingLog
from cc.libs.utils import get_domain
from cc.libs.exceptions import MessageExpired

from templated_email import send_templated_mail
from datetime import datetime, timedelta, date
import json


def get_message(id, user):
    '''
    Get message if the user has permission to view it
    '''
    if id:
        message = get_object_or_404(Message, pk=id)
        if message.is_available_for_user(user):
            if message.expired_at < datetime.now():
                raise MessageExpired
            else:
                return message
        else:
            raise PermissionDenied


def _create_ocl_link(user, domain, message_id):
    # token should be expired after 30 days
    ocl = OneClickLinkToken.objects.create(
        user=user,
        expires_on=date.today() + timedelta(days=30)
    )

    # create the OCL link and return
    return '{}/view/{}/?token={}'.format(
        domain, message_id, ocl.token
    )


def _replace_link_text(message, ocl_link):
    link_text = message.link_text
    if link_text == '':
        link_text = ocl_link

    return message.message.replace(
        '[link1]',
        u'<a href="{0}">{1}</a>'.format(ocl_link, link_text)
    )


def _send_message(message, recipient, domain):
    ocl_link = _create_ocl_link(recipient, domain, message.id)

    # replace the token [link1] with the actual OCL link
    text = _replace_link_text(message, ocl_link)

    # create tracking pixel
    tracking_pixel_src = '{}/track/email/{}/{}/'.format(
        domain, message.id, recipient.id
    )

    send_templated_mail(
        template_name='message_default',
        from_email=message.owner.email,
        recipient_list=[recipient.email],
        context={
            'message': message,
            'text': text,
            'tracking_pixel_src': tracking_pixel_src
        },
        headers={
            'X-SMTPAPI': json.dumps({
                'unique_args': {
                    'cc_message_id': message.id,
                    'domain': domain
                }
            })
        }
    )


def create_ocl_and_send_message(message, domain):
    '''
    Create OCL link (to the message) for each recipients and send email to them
    '''
    recipient_emails = []

    for r in message.receivers.all():
        _send_message(message, r, domain)

        # add recipient email address to the list
        recipient_emails.append(r.email)

    # send a copy if sender chooses to cc himself
    if message.cc_me:
        # create ocl link for message owner
        ocl_link = _create_ocl_link(message.owner, domain, message.id)

        # add OCL link to email text
        text = _replace_link_text(message, ocl_link)

        # and send
        send_templated_mail(
            template_name='message_cc',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.owner.email],
            context={
                'message': message,
                'text': text,
                'recipients': ', '.join(recipient_emails),
            },
        )


def send_notification_email(reason_code, message, recipient=None):
    '''
    Send notification email to sender, log the action if not exist
    reason_code 1: email is opened
    reason_code 2: link is clicked
    reason_code 3: conversion error
    '''
    if reason_code == 1:
        action = TrackingLog.OPEN_EMAIL_ACTION
        subject = _('[Notification] %s opened your email.') % recipient.email
        email_template = 'notification_email_opened'
    elif reason_code == 2:
        action = TrackingLog.CLICK_LINK_ACTION
        subject = _(
            '[Notification] %s clicked on your link.'
        ) % recipient.email
        email_template = 'notification_link_clicked'
    elif reason_code == 3:
        subject = _('[Notification] Conversion error.')
        email_template = 'notification_conversion_error'
    else:
        return None

    # check if email has been sent
    should_send = True
    log = None
    if reason_code in [1, 2] and recipient:
        # if there is existing log then should not send email again
        if TrackingLog.objects.filter(
            message=message,
            participant=recipient,
            action=action
        ):
            should_send = False

        # check if the setting is on
        if not (
            (reason_code == 1 and message.notify_email_opened)
            or (reason_code == 2 and message.notify_link_clicked)
        ):
            should_send = False

        # create log anyway
        log = TrackingLog.objects.create(
            message=message,
            participant=recipient,
            action=action,
            revision=2
        )

    # then send email if needed
    if should_send:
        send_templated_mail(
            template_name=email_template,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.owner.email],
            context={
                'subject': subject,
                'message_subject': message.subject,
                'recipient': getattr(recipient, 'email', None),
            },
        )

    return log


def notify_email_opened(message_id, user_id):
    if message_id > 0 and user_id > 0:
        qs = Message.objects.filter(id=message_id, receivers=user_id)
        if qs:
            message = qs[0]
            recipient = CUser.objects.get(id=user_id)
            send_notification_email(1, message, recipient)
        else:
            return False
    else:
        return False


def edit_email_and_resend_message(request, message):
    domain = get_domain(request)
    new_email = request.POST.get('new_email')
    old_email = request.POST.get('old_email')
    user_id = request.POST.get('user_id')

    if user_id:
        rec = CUser.objects.get(pk=int(user_id))
        _send_message(message, rec, domain)
    else:
        recipient = CUser.objects.filter(email=old_email)
        if recipient:
            exist_user = CUser.objects.filter(email=new_email)
            if exist_user:
                rec = exist_user[0]
                message.receivers.remove(recipient[0])
                message.receivers.add(rec)
            else:
                rec = recipient[0]
                # save the new email for that recipient and resend the message
                rec.email = new_email
                rec.save()

            _send_message(message, rec, domain)

            # clear record from bounce
            bounce = Bounce.objects.filter(message=message, email=old_email)
            bounce.delete()
