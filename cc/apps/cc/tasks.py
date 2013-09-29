from celery.decorators import task

from .services import create_ocl_and_send_message
#from cc.apps.content.models import File
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

@task
def send_cc_message(convert_result, message, domain):
    if (convert_result):
        create_ocl_and_send_message(message, domain)
    else:
        print 'TODO FAIL'