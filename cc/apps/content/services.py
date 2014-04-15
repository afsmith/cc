from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import File
from cc.libs import utils

from os import path
from PyPDF2 import PdfFileReader
from urlparse import urljoin
import datetime


def save_pdf(user, orig_filename, coping_file_callback):
    '''
    Save the uploaded file and return the status and file meta data
    '''
    if not File.is_supported_file(orig_filename):
        return {
            'status': 'ERROR',
            'message': unicode(_('Unsupported file type.')),
            'file_id': None
        }

    file = File(orig_filename=orig_filename, owner=user)

    full_orig_file_path = path.join(
        settings.CONTENT_UPLOADED_DIR,
        file.orig_file_path
    )
    coping_file_callback(full_orig_file_path)

    try:
        file.type = File.type_from_name(full_orig_file_path)
    except utils.UnsupportedFileTypeError:
        return {
            'status': 'ERROR',
            'message': unicode(_('Unsupported file type.')),
            'file_id': file.id
        }

    # get the page count
    file_abs_path = path.abspath(path.join(
        settings.MEDIA_ROOT, full_orig_file_path
    ))
    try:
        pdf = PdfFileReader(open(file_abs_path, 'rb'))
        file.pages_num = pdf.getNumPages()
    except IOError:
        # Testing eh?
        file.pages_num = 7

    file.save()

    # if exceed max pages in settings
    if file.pages_num > settings.PDF_MAX_PAGES:
        return {
            'status': 'ERROR',
            'message': unicode(_(
                'The PDF has too many pages.'
                ' Attachment should be maximum {} pages'.format(
                    settings.PDF_MAX_PAGES
                )
            )),
            'file_id': file.id
        }

    # if everything is cool
    return {
        'status': 'OK',
        'file_id': file.id,
        'file_orig_filename': file.orig_filename,
        'file_type': file.type,
        'page_count': file.pages_num
    }


def save_uploaded_image(file, domain):
    if not File.is_supported_file(file.name):
        return {
            'status': 'ERROR',
            'message': unicode(_('Unsupported file type.'))
        }

    original_name, file_extension = path.splitext(file.name)
    filename = '{}{}{}'.format(
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        utils.gen_file_key(),
        file_extension
    )
    url = path.join(settings.SUMMERNOTE_FILE_DIR, filename)
    file_abs_path = path.abspath(path.join(
        settings.MEDIA_ROOT, url
    ))
    destination = open(file_abs_path, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

    return {
        'status': 'OK',
        'url': urljoin(urljoin(domain, settings.MEDIA_URL), url)
    }
