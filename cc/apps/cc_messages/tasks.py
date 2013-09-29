from celery.decorators import task

from .services import create_ocl_and_send_message, send_notification_email
from cc.apps.content.tasks import process_stored_file
from cc.libs.utils import get_domain


def process_file_and_send_message(message, request):
    domain = get_domain(request)
    file = message.files.all()[0]
    chain = (
        process_stored_file.s(file) 
        | send_cc_message.s(message, domain)
    )
    try:
        chain()
    except Exception, e:
        print '[CELERY TASK ERROR] %s' % e
        # if converion goes wrong, send notification to sender
        send_notification_email(3, message)

@task
def send_cc_message(convert_result, message, domain):
    if (convert_result):
        create_ocl_and_send_message(message, domain)
    else:
        # if converion goes wrong, send notification to sender
        send_notification_email(3, message)