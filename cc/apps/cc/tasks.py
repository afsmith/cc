#from __future__ import absolute_import

from celery.decorators import task

from .services import create_ocl_and_send_message
from cc.apps.content.models import File
from cc.apps.content.tasks import process_stored_file
from cc.libs.utils import get_domain


def process_file_and_send_message(course, request, message):
    domain = get_domain(request)
    if message is None:
        message = course.message
    file = File.objects.get(pk=message.attachment)
    chain = (
        process_stored_file.s(file) 
        | send_cc_message.s(course, domain, message)
    )
    try:
        chain()
    except Exception, e:
        print '[CELERY TASK ERROR] %s' % e

@task
def send_cc_message(convert_result, course, domain, message):
    if (convert_result):
        create_ocl_and_send_message(course, domain, message)
    else:
        print 'TODO FAIL'