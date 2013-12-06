from django.core.files import storage

from cc.apps.content.models import File
from cc.apps.accounts.models import OneClickLinkToken

from celery.decorators import task
from datetime import datetime, timedelta


@task
def delete_old_content():
    '''
    Periodical task to remove old content
    '''

    # after 90 days, remove the original raw PDFs
    files_90_days = File.objects.filter(
        created_on__lt=datetime.today()-timedelta(days=90),
    )
    for file in files_90_days:
        if storage.default_storage.exists(file.orig_file_path):
            storage.default_storage.delete(file.orig_file_path)

    # after 120 days, remove the converted versions and the file rows
    files_120_days = File.objects.filter(
        created_on__lt=datetime.today()-timedelta(days=120),
    )
    for file in files_120_days:
        if storage.default_storage.exists(file.conv_file_path):
            storage.default_storage.delete(file.conv_file_path)

    # after 120 days, remove the expired OCLs
    ocls = OneClickLinkToken.objects.filter(
        expires_on__lt=datetime.today()-timedelta(days=90),
    ).delete()