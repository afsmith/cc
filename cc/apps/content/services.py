from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mass_mail
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import utils, tasks
from .models import File, Course
from cc.apps.accounts.services import create_group
from cc.apps.accounts.models import OneClickLinkToken

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

    if file.status == File.STATUS_UPLOADED:
        tasks.process_stored_file.delay(file)

    return {
        'status': 'OK',
        'file_id': file.id,
        'file_orig_filename': file.orig_filename,
        'file_type': file.type,
    }


def create_course_from_message(message):
    group = create_group(message.receivers.all())

    course = Course.objects.create(
        title=File.objects.get(pk=message.attachment).key,
        owner=message.owner,
        group=group
    )
    course.files.add(message.attachment)
    course.save()

    return course


def create_ocl_and_send_mail(course, receipients, request):
    host = request.get_host() # Todo
    emails = ()
    for r in receipients:
        ocl = OneClickLinkToken.objects.create(user=r)
        
        ocl_link = 'http://%s/content/view/%d/?token=%s' % (
            host, course.id, ocl.token
        )
        emails += ((
            'Subject OCL', 'Body %s' % ocl_link, course.owner.email, [r.email]
        ),)

    send_mass_mail(emails)


def check_course_permission(id, user):
    if id:
        course = get_object_or_404(Course, pk=id)
        if course.is_available_for_user(user):
            return course
        else:
            raise PermissionDenied
