from django.core.urlresolvers import reverse
from django.core.files import storage
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

from .forms import FileImportForm
from .services import save_file, check_course_permission
from cc.apps.accounts.services import verify_ocl_token
from cc.apps.cc.services import send_notification_email

from annoying.decorators import ajax_request, render_to
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


@render_to('content/view_course.html')
def view_course(request, id=None):
    token = request.GET.get('token')
    if token:
        ocl_token = verify_ocl_token(token)
        if not ocl_token:
            return {
                'ocl_expired': True
            }
        course = check_course_permission(id, ocl_token.user)

        # there is only 1 file per course for now so return that file
        file = course.files.all()[0]
        pages_num = file.pages_num
        view_url = file.view_url
        page_list = []

        if pages_num == 1:
            page_list.append('%s/p.png' % view_url)
        elif pages_num > 1:
            for i in range(0, pages_num):
                page_list.append('%s/p-%d.png' % (view_url, i))

        # notify the sender if "notify when link clicked" option is on
        if course.message.notify_link_clicked:
            send_notification_email(course, ocl_token.user, 2)

        return {
            'course': course,
            'page_list': page_list,
            'token': token,
        }
    else:
        return redirect(reverse('home'))
