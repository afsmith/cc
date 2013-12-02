from django.core.files import storage

from cc.apps.content import convert

from celery.decorators import task
from celery.utils.log import get_task_logger


@task
def process_stored_file(file):
    logger = get_task_logger(__name__)
    conv = convert.get_converter(file, storage.default_storage, logger)
    try:
        conv.convert()
    except convert.ConversionError, e:
        print '[CONVERSION ERROR] %s' % e
        return False
    return True
