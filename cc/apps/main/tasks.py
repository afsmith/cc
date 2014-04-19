from django.core.files import storage
from django.conf import settings

from cc.apps.content.models import File
from cc.apps.accounts.models import OneClickLinkToken

from celery.decorators import task
from datetime import datetime, timedelta


@task
def delete_old_content():
    '''
    Periodical task to remove old content
    '''

    '''
    # remove the original raw PDFs 30 days before message expire
    old_original_files = File.objects.filter(
        created_on__lt=datetime.today() - timedelta(
            days=settings.MESSAGE_EXPIRED_AFTER - 30
        )
    )
    for file in old_original_files:
        if storage.default_storage.exists(file.orig_file_path):
            storage.default_storage.delete(file.orig_file_path)

    # remove the converted versions when message expire
    old_converted_files = File.objects.filter(
        created_on__lt=datetime.today() - timedelta(
            days=settings.MESSAGE_EXPIRED_AFTER
        )
    )
    for file in old_converted_files:
        if storage.default_storage.exists(file.conv_file_path):
            storage.default_storage.delete(file.conv_file_path)
    '''

    # after 120 days, remove the expired OCLs
    OneClickLinkToken.objects.filter(
        expires_on__lt=datetime.today() - timedelta(days=120),
    ).delete()
