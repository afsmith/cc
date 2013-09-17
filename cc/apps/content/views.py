from django import http
from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.utils.translation import ugettext_lazy as _
from django.core.files import storage
from django.shortcuts import redirect

from . import serializers
from .forms import FileImportForm
from .services import save_file, check_course_permission
from cc.apps.accounts.services import verify_ocl_token
from cc.libs import decorators as custom_decorators
from cc.libs import bls_django

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


@custom_decorators.login_or_token_required
@render_to('content/view_course.html')
def view_course(request, id=None):
    #if request.user.is_authenticated():
    #    return HttpResponseRedirect(reverse('content-view_module', kwargs={'id': id}))

    token = request.GET.get('token')
    if token:
        ocl_token = verify_ocl_token(token)
        if not ocl_token:
            return redirect('/')
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

        return {
            'course': course,
            'page_list': page_list,
            'token': token,
        }


@custom_decorators.login_or_token_required
@http_decorators.require_GET
def module_descr(request, id):
    """Creates module description.
    """

    user = request.user
    format = request.GET.get('format', 'json')
    token = request.GET.get('token')
    if token:
        ocl_token = verify_ocl_token(token)
        if not ocl_token or ocl_token.expired:
            return redirect('/')

        user = ocl_token.user
        course = check_course_permission(id, user)

    if format == 'json':
        return bls_django.HttpJsonResponse(serializers.serialize_course(
            course, user, tracking=None, ocl_token=token
        ))

    return http.HttpResponseNotFound('Requested module not found.')

'''
@auth_decorators.login_required
def view_module(request, id=None):
    if id is not None:
        course = get_object_or_404(models.Course, pk=id)
        if not course.is_available_for_user(request.user):
            raise Http403
            return render_to_response()
    
    ctx = {'course': course}
    
    show_sign_off_button = False
    if module_with_track_ratio(request.user.id, course.id) == 1 and\
            course.sign_off_required:
        try:
            course_user = CourseUser.objects.get(course=course,
                    user=request.user)
        except CourseUser.DoesNotExist:
            show_sign_off_button = True
    
    ctx['show_sign_off_button'] = _show_sign_off_button(request.user, course)
    return direct_to_template(request, 'content/module_viewer.html', ctx)
'''
