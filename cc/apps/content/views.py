from django.core.files import storage
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.http import HttpResponse

from .forms import FileImportForm
from .services import save_pdf, save_uploaded_image
from .models import File
from cc.apps.tracking.services import create_tracking_log
from cc.libs.utils import get_domain, DotExpandedDict

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
        return save_pdf(
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


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def upload_image(request):
    domain = get_domain(request)
    return save_uploaded_image(request.FILES.get('file'), domain)


@auth_decorators.login_required
@http_decorators.require_POST
@ajax_request
def save_file_info(request):
    params = DotExpandedDict(request.POST)
    for k in params.keys():
        try:
            f = File.objects.get(pk=int(k))
        except File.DoesNotExist:
            print 'File {} doesnt exist'.format(k)
            continue
        else:
            f.index = params[k].get('index')
            f.link_text = params[k].get('value')
            f.save()
    return {}


def download_file(request, file_id):
    try:
        f = File.objects.get(pk=file_id)
    except File.DoesNotExist:
        return HttpResponse()

    file_stream = open(f.orig_file_abspath, 'r')
    response = HttpResponse(
        file_stream.read(),
        mimetype='application/octet-stream'  # 'application/force-download'
    )
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        smart_str(f.orig_file_path)
    )

    # create the tracking log
    message_id = request.GET.get('message')
    user_id = request.GET.get('user')
    create_tracking_log(
        message=message_id,
        participant=user_id,
        action='DOWNLOAD',
        file_index=f.index,
    )

    return response
