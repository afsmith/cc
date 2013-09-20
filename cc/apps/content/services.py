from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import utils, tasks, convert
from .models import File, Course
from cc.apps.accounts.services import create_group

import os


def save_file(user, orig_filename, coping_file_callback):
    '''
    Save the uploaded file and return the status and file meta data
    '''
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

    # if file is uploaded, start the celery conversion task
    if file.status == File.STATUS_UPLOADED:
        try:
            tasks.process_stored_file.delay(file)
        except convert.ConversionError, e:
            return {
                'status': 'ERROR',
                'message': unicode(_('File conversion error.')),
                'original_error': e
            }
        except Exception, e:
            # catch all other errors here to not display anything for end user
            return {
                'status': 'ERROR',
                'message': unicode(_(
                    'Something went wrong. Please contact the admin.'
                )),
                'original_error': e.__str__()
            }

    return {
        'status': 'OK',
        'file_id': file.id,
        'file_orig_filename': file.orig_filename,
        'file_type': file.type,
    }


def create_course_from_message(message):
    '''
    Create the group and course from the message
    '''
    group = create_group(message.receivers.all())

    course = Course.objects.create(
        title=message.subject,
        owner=message.owner,
        group=group
    )
    course.files.add(message.attachment)
    course.save()

    return course


def check_course_permission(id, user):
    '''
    Check if the user has permission to view the course
    '''
    if id:
        course = get_object_or_404(Course, pk=id)
        if course.is_available_for_user(user):
            return course
        else:
            raise PermissionDenied
