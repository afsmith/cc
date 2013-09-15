from django.contrib.auth import decorators as auth_decorators
from django.views.decorators import http as http_decorators
from django.utils.translation import ugettext_lazy as _
from django.core.files import storage
from django.shortcuts import redirect

from .forms import FileImportForm
from .services import save_file, check_course_permission
from cc.apps.accounts.services import verify_ocl_token
from cc.libs import decorators as custom_decorators

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
        
        return {
            'course': course,
            'token': token,
        }

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
