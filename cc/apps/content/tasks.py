from django.core.files import storage

from cc.apps.content import convert, models

from celery.decorators import task
from celery.utils.log import get_task_logger
import datetime


@task(ignore_result=True)
def process_stored_file(file):
    logger = get_task_logger(__name__)
    conv = convert.get_converter(file, storage.default_storage, logger)
    conv.convert()


@task
def delete_expired_content():
    """Task realising periodic removal of content for outdated files.
    """

    # setting status STATUS_EXPIRED to files with past expires_on
    models.File.objects.filter(
        expires_on__isnull=False,
        expires_on__lt=datetime.date.today(),
        is_removed=False
    ).exclude(
        status__in=(models.File.STATUS_EXPIRED, models.File.STATUS_REMOVED)
    ).update(status=models.File.STATUS_EXPIRED)

    # removing files with status = STATUS_INVALID
    models.File.objects.filter(status=models.File.STATUS_INVALID).delete()

    # removing expired files not associated with any segment
    to_delete = models.File.objects.filter(
        expires_on__isnull=False,
        expires_on__lt=datetime.date.today(),
        delete_expired=True,
        is_removed=False,
    ).exclude(
        id__in=models.Segment.objects.values_list('file__id', flat=True)
    )
    for file in to_delete:
        if storage.default_storage.exists(file.conv_file_path):
            storage.default_storage.delete(file.conv_file_path)
        if storage.default_storage.exists(file.orig_file_path):
            storage.default_storage.delete(file.orig_file_path)
    to_delete.delete()

    # removing content from expired files associated with segment
    to_delete = models.File.objects.filter(
        expires_on__isnull=False,
        expires_on__lt=datetime.date.today(),
        delete_expired=True,
        is_removed=False
    )
    for file in to_delete:
        if storage.default_storage.exists(file.conv_file_path):
            storage.default_storage.delete(file.conv_file_path)
        if storage.default_storage.exists(file.orig_file_path):
            storage.default_storage.delete(file.orig_file_path)
        file.is_removed = True
        file.status = models.File.STATUS_REMOVED
        file.save()
