from django.core.mail import send_mail, send_mass_mail
from django.conf import settings

from cc.apps.accounts.models import OneClickLinkToken

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


def create_ocl_and_send_mail(course, request, message=None):
    '''
    Create OCL link (to the course) for each recipients and send email to them
    '''
    emails = ()
    recipient_emails = []
    if not message:
        message = course.message

    for r in message.receivers.all():
        # ocl token should expire after 30 days
        ocl = OneClickLinkToken.objects.create(
            user=r,
            expires_on=datetime.datetime.today() + datetime.timedelta(days=30)
        )
        ocl_link = 'http://%s/content/view/%d/?token=%s' % (
            request.get_host(), course.id, ocl.token
        )

        # email tuple format: (subject, message, from_email, recipient_list)
        emails += ((
            message.subject,
            EMAIL_TEMPLATE % {'message': message.message, 'ocl_link': ocl_link},
            course.owner.email,
            [r.email]
        ),)

        recipient_emails.append(r.email)

    # if sender chooses to cc himself
    if message.cc_me:
        emails += ((
            message.subject,
            CC_ME_TEMPLATE % {
                'recipients': ', '.join(recipient_emails),
                'message': message.message
            },
            settings.DEFAULT_FROM_EMAIL,
            [course.owner.email]
        ),)

    # send mass / bulk emails to be more efficient
    send_mass_mail(emails)


def send_notification_email(course, recipient, reason_code):
    '''
    Send notification email to sender
    reason_code 1: notify_email_opened
    reason_code 2: notify_link_clicked
    '''
    message = course.message
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
        recipient_list=[course.owner.email]
    )
