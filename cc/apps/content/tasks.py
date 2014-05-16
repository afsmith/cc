from django.core.files import storage

from cc.apps.content import convert

from celery.decorators import task
from celery.utils.log import get_task_logger


@task
def process_stored_files(files):
    logger = get_task_logger(__name__)
    for f in files:
        conv = convert.get_converter(f, storage.default_storage, logger)
        try:
            conv.convert()
        except convert.ConversionError, e:
            print '[CONVERSION ERROR] %s' % e
            return False
    return True
