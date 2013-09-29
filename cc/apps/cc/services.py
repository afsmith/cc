from django.conf import settings
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives

from cc.apps.accounts.models import OneClickLinkToken, CUser
from cc.apps.cc_messages.models import Message

import datetime

EMAIL_TEMPLATE = '''%(message)s.

Click here to check the file: %(ocl_link)s'''

CC_ME_TEMPLATE = '''Here is a copy of the message you sent to: %(recipients)s.
------------------------------------------------

%(message)s.

Click here to check the file: [link]'''

NOTIFICATION_EMAIL_OPENED_TEMPLATE = '''%(recipient)s opened your email "%(subject)s".

If you selected to be notified when they look at your attachment we'll send you another email at that time.

Good closings to you.

Best,
Kneto'''

NOTIFICATION_LINK_CLICKED_TEMPLATE = '''%(recipient)s checked your attachment from email "%(subject)s."

Good closings to you.

Best,
Kneto'''


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

        text_body = EMAIL_TEMPLATE % {
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
            body=CC_ME_TEMPLATE % {
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


def send_notification_email(message, recipient, reason_code):
    '''
    Send notification email to sender
    reason_code 1: notify_email_opened
    reason_code 2: notify_link_clicked
    '''
    if reason_code == 1:
        subject = '[Notification] %s opened your email.' % recipient.email
        body = NOTIFICATION_EMAIL_OPENED_TEMPLATE % {
            'recipient': recipient.email,
            'subject': message.subject
        }
    elif reason_code == 2:
        subject = '[Notification] %s clicked on your link.' % recipient.email
        body = NOTIFICATION_LINK_CLICKED_TEMPLATE % {
            'recipient': recipient.email,
            'subject': message.subject
        }
    else:
        return None

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
                send_notification_email(message, recipient, 1)
        else:
            return False
    else:
        return False
