from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mass_mail
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import utils, tasks
from .models import File, Course
from .convert import ConversionError
from cc.apps.accounts.services import create_group
from cc.apps.accounts.models import OneClickLinkToken

import os
import datetime


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
        except:
            print 'huhu'

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


def create_ocl_and_send_mail(course, message, request):
    '''
    Create OCL link (to the course) for each recipients and send email to them
    '''
    # extract the domain name from request
    domain = request.get_host()
    emails = ()
    for r in message.receivers.all():
        # ocl token should expire after 30 days
        ocl = OneClickLinkToken.objects.create(
            user=r,
            expires_on=datetime.datetime.today() + datetime.timedelta(days=30)
        )
        ocl_link = 'http://%s/content/view/%d/?token=%s' % (
            domain, course.id, ocl.token
        )

        # email tuple format: (subject, message, from_email, recipient_list)
        emails += ((
            message.subject,
            '%s. Click here to check the file %s' % (message.message, ocl_link),
            course.owner.email,
            [r.email]
        ),)

    # if sender chooses to cc himself
    if message.cc_me:
        emails += ((
            message.subject,
            '%s. Click here to check the file [link]' % message.message,
            course.owner.email,  # TODO: might change to system email address
            [course.owner.email]
        ),)

    # send mass / bulk emails to be more efficient
    send_mass_mail(emails)


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
