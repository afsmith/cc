from django.core.mail import send_mass_mail
from django.conf import settings

from cc.apps.accounts.models import OneClickLinkToken

import datetime

EMAIL_TEMPLATE = '''%(message)s.

Click here to check the file: %(ocl_link)s'''

CC_ME_EMAIL_TEMPLATE = '''Here is a copy of the message you sent to: %(recipients)s.
------------------------------------------------

%(message)s.

Click here to check the file: [link]'''


def create_ocl_and_send_mail(course, message, request):
    '''
    Create OCL link (to the course) for each recipients and send email to them
    '''
    # extract the domain name from request
    domain = request.get_host()
    emails = ()
    recipient_emails = []
    for r in message.receivers.all():
        # ocl token should expire after 30 days
        ocl = OneClickLinkToken.objects.create(
            user=r,
            expires_on=datetime.datetime.today() + datetime.timedelta(days=30)
        )
        ocl_link = 'http://%s/content/view/%d/?token=%s' % (
            domain, course.id, ocl.token
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
            CC_ME_EMAIL_TEMPLATE % {
                'recipients': ', '.join(recipient_emails),
                'message': message.message
            },
            settings.DEFAULT_FROM_EMAIL,
            [course.owner.email]
        ),)

    # send mass / bulk emails to be more efficient
    send_mass_mail(emails)
