from django.core.files import storage
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.utils.translation import ugettext_lazy as _

from .forms import FileImportForm
from .services import save_file
from .models import File

from annoying.decorators import ajax_request
from contextlib import closing


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def upload_file(request):
    form = FileImportForm(request.POST, request.FILES)
    if form.is_valid():
        def coping_file_callback(full_orig_file_path):
            with closing(
                storage.default_storage.open(full_orig_file_path, 'wb')
            ) as fh:
                for chunk in form.cleaned_data['file'].chunks():
                    fh.write(chunk)
        return save_file(
            request.user,
            form.cleaned_data['file'].name,
            coping_file_callback
        )
    return {
        'status': 'ERROR',
        'message': unicode(_('Exceeded maximum file upload size.'))
    }


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def remove_file(request, file_id):
    File.objects.filter(pk=file_id).delete()
    return {}