from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from . import utils
from .models import File

from os import path
from PyPDF2 import PdfFileReader


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
            'message': unicode(_('Unsupported file type.'))
        }

    file.save()

    # get the page count
    file_abs_path = path.abspath(path.join(
        settings.MEDIA_ROOT, full_orig_file_path
    ))
    try:
        pdf = PdfFileReader(open(file_abs_path, 'rb'))
        page_count = pdf.getNumPages()
    except IOError:
        # Testing eh?
        page_count = -1

    # if exceed max pages in settings
    if page_count > settings.PDF_MAX_PAGES:
        return {
            'status': 'ERROR',
            'message': unicode(_('The attachment has too many pages.'))
        }

    # if everything is cool
    return {
        'status': 'OK',
        'file_id': file.id,
        'file_orig_filename': file.orig_filename,
        'file_type': file.type,
        'page_count': page_count
    }
