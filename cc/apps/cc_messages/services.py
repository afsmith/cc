from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Message, Link
from cc.apps.reports.models import Bounce
from cc.apps.accounts.models import OneClickLinkToken, CUser
from cc.apps.tracking.models import TrackingLog
from cc.apps.tracking.services import create_tracking_log
from cc.libs.utils import get_domain
from cc.libs.exceptions import MessageExpired

from templated_email import send_templated_mail
from datetime import datetime, timedelta, date
import json
import re

url_regex = re.compile(r'<a href="?\'?([^"\'>]*)')


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


def _replace_links(message, domain):
    def replace(match):
        groups = match.groups()
        link, created = Link.objects.get_or_create(original_url=groups[0])
        return '<a href="{}/track/link/{}/{}/'.format(
            domain, message.id, link.converted_key
        )
    return url_regex.subn(replace, message.message)


def _create_ocl_link_replace_link_texts(message, user, domain):
    # replace all links
    text, count = _replace_links(message, domain)

    # save the external link count
    message.external_links = count
    message.save()

    # token should be expired after 30 days
    ocl = OneClickLinkToken.objects.create(
        user=user,
        expires_on=date.today() + timedelta(days=30)
    )

    # loop through all files of message
    for f in message.files.all():
        # create the OCL link
        ocl_link = '{}/view/{}/{}/?token={}'.format(
            domain, message.id, f.index, ocl.token
        )

        # get link text for each file
        link_text = f.link_text
        if link_text == '':
            link_text = ocl_link

        # and replace the token
        text = text.replace(
            '[link{}]'.format(f.index),
            u'<a href="{}">{}</a>'.format(ocl_link, link_text)
        )
    return text


def _send_message(message, recipient, domain):
    text = _create_ocl_link_replace_link_texts(message, recipient, domain)

    # create tracking pixel
    tracking_pixel_src = '{}/track/email/{}/{}/'.format(
        domain.replace('https', 'http'), message.id, recipient.id
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
        text = _create_ocl_link_replace_link_texts(
            message, message.owner, domain
        )

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


def send_notification_email(
    reason_code, message, recipient=None, file_index=None, request=None
):
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
        # if this is open email action, set the file_index to 0
        if reason_code == 1:
            file_index = 0

        # if there is existing log then should not send email again
        if TrackingLog.objects.filter(
            message=message,
            participant=recipient,
            action=action,
            file_index=file_index,
        ):
            should_send = False

        # check if the setting is on
        if not (reason_code == 1 or reason_code == 2):
            should_send = False

        # create log anyway
        log = create_tracking_log(
            message=message,
            participant=recipient,
            action=action,
            file_index=file_index,
            request=request
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


def notify_email_opened(message_id, user_id, request):
    if message_id > 0 and user_id > 0:
        qs = Message.objects.filter(id=message_id, receivers=user_id)
        if qs:
            message = qs[0]
            recipient = CUser.objects.get(id=user_id)
            send_notification_email(
                1, message, recipient, request=request
            )
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
        # resend message to one user
        rec = CUser.objects.get(pk=int(user_id))
        _send_message(message, rec, domain)
    elif new_email:
        # edit email address and resend message
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
    else:
        # resend the original message to all recipients
        create_ocl_and_send_message(message, domain)
