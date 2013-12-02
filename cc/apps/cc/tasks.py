from django.core.files import storage

from cc.apps.content.models import File

from celery.decorators import task
import datetime


@task
def delete_old_content():
    '''
    Periodical task to remove old content
    '''

    # setting status STATUS_EXPIRED to files with past expires_on
    File.objects.filter(
        expires_on__isnull=False,
        expires_on__lt=datetime.date.today(),
        is_removed=False
    ).exclude(
        status__in=(File.STATUS_EXPIRED, File.STATUS_REMOVED)
    ).update(status=File.STATUS_EXPIRED)

    # removing files with status = STATUS_INVALID
    File.objects.filter(status=File.STATUS_INVALID).delete()

    # removing expired files not associated with any segment
    to_delete = File.objects.filter(
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
    to_delete = File.objects.filter(
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
        file.status = File.STATUS_REMOVED
        file.save()