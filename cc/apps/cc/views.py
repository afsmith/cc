from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.core.files import storage
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cc.apps.content import utils
from cc.apps.content.models import File
from cc.apps.content.forms import FileImportForm
from cc.apps.cc_messages.forms import MessageForm

from annoying.decorators import render_to, ajax_request
from contextlib import closing
import os


@auth_decorators.login_required
@render_to('cc/message.html')
def home(request):
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            # TODO
            # 1. create a course out of the POST request
            # 2. create users from receivers field
            # 3. assign course to users / group
            # 4. create OCL link
            # 5. send email
            pass
    else:
        message_form = MessageForm()

    return {
        'message_form': message_form,
        'import_file_form': FileImportForm(),
    }


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def upload_file(request):
    form = FileImportForm(request.POST, request.FILES)
    if form.is_valid():
        def coping_file_callback(full_orig_file_path):
            with closing(storage.default_storage.open(full_orig_file_path, 'wb')) as fh:
                for chunk in form.cleaned_data['file'].chunks():
                    fh.write(chunk)
        return _save_uploaded_file(
            request.user,
            form.cleaned_data['file'].name,
            coping_file_callback
        )
    return {
        'status': 'ERROR',
        'message': unicode(_('Exceeded maximum file upload size.'))
    }


def _save_uploaded_file(user, orig_filename, coping_file_callback):
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

    if file.type == File.TYPE_IMAGE:
        lang = ''
    else:
        lang = user.get_profile().language

    is_duration_visible = not file.type in [File.TYPE_AUDIO, File.TYPE_VIDEO]
    return {
        'status': 'OK',
        'file_id': file.id,
        'file_orig_filename': file.orig_filename,
        'selected_language': lang,
        'file_type': file.type,
        'is_duration_visible': is_duration_visible
    }
