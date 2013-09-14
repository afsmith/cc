from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from . import utils
from .models import File, Course

import os


def save_file(user, orig_filename, coping_file_callback):
    if not File.is_supported_file(orig_filename):
        return {
            'status': 'ERROR',
            'message': unicode(_('Unsupported file type.'))
        }

    file = File(orig_filename=orig_filename)

    full_orig_file_path = os.path.join(
        settings.CONTENT_UPLOADED_DIR,
        file.orig_file_path
    )
    coping_file_callback(full_orig_file_path)

    try:
        file.type = File.type_from_name(full_orig_file_path)
    except utils.UnsupportedFileTypeError:
        return {
            'status': 'ERROR',
            'message': unicode(_('Unsupported file type.'))
        }

    file.save()

    is_duration_visible = not file.type in [File.TYPE_AUDIO, File.TYPE_VIDEO]
    return {
        'status': 'OK',
        'file_id': file.id,
        'file_orig_filename': file.orig_filename,
        'file_type': file.type,
        'is_duration_visible': is_duration_visible
    }


def create_course(message, group):
    Course.objects.create(
        title=File.objects.get(pk=message.attachment).key,
        file=File.objects.get(pk=message.attachment),
        owner=message.owner,
        group=group
    )
