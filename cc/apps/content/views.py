# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Django views.
"""
from __future__ import absolute_import

from copy import deepcopy
import calendar, datetime, json, os, StringIO
from contextlib import closing
import mimetypes

from django import http
import django
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import models as auth_models, decorators as auth_decorators
from django.contrib.syndication.views import Feed
from django.core import paginator
from django.core import urlresolvers
from django.core.files import storage
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import conditional_escape
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators import http as http_decorators
from django.shortcuts import render
import re
#from administration.models import get_entry_val, ConfigEntry

from distutils import file_util

from cc.libs.bls_common import bls_django
from cc.libs.bls_common.bls_django import HttpJsonOkResponse, HttpJsonResponse
from cc.apps.content.course_states import InvalidActionError, Active, ActiveAssign, Draft, ActiveInUse, Deactivated, DeactivatedUsed, CourseState
from cc.apps.content.models import Course, CourseGroup, CourseUser, CourseGroupCanBeAssignedTo, Segment, DownloadEvent, File
#from administration.models import ConfigEntry
from cc.apps.content.serializers import _get_language_name
from cc.apps.management import models as manage_models
from cc.apps.management.models import OneClickLinkToken
from cc.libs.plato_common import decorators
from cc.libs.plato_common.middleware import Http403
#from tagging.utils import bind_tags_with_file, add_if_not_exist
from cc.apps.tracking.models import TrackingEventService, module_with_track_ratio
#from reports import reports

#from tagging import models as tagging_models

from cc.apps.content import forms
from cc.apps.content import models
from cc.apps.content import serializers
from cc.apps.content import tasks
from cc.apps.content import utils

#from messages_custom.models import MailTemplate

@auth_decorators.login_required
def list_modules(request):
    courses = models.Course.objects.all()

    return render(request, 'content/list_modules.html', {
        'courses': courses,
        'show_sign_off': getattr(settings, 'SIGN_OFF_ON_MODULE', False)
        })

def _get_can_be_assigned_to_groups(user):
    if user.get_profile().is_admin:
        return [], user.groups.all()
    elif user.get_profile().is_superadmin:
        return auth_models.Group.objects.all(), user.groups.all()
    
@auth_decorators.login_required
@decorators.is_admin_or_superadmin
def manage_modules(request):
    
    """ Handling EditModuleForm should be placed here
    """
    groups, my_groups = _get_can_be_assigned_to_groups(request.user)
    if request.method == "GET":
        return render(request, 'content/list_modules.html', {
            'form': forms.EditModuleForm(),
            'manageModulesForm': forms.ManageModulesForm(initial={'owner': request.user}),
            'groups': groups,
            'my_groups': my_groups,
            'show_sign_off': getattr(settings, 'ENABLE_MODULES_SIGNOFF', False),
            'settings': {'SALES_PLUS': settings.SALES_PLUS},
            })
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    course = Course.objects.get(id=data['module_id'])
    course.title = data.get('title', course.title)
    course.objective = data.get('objective', course.objective)
    course.completion_msg = data.get('completion_msg')
    course.allow_download = data.get('allow_download', course.allow_download)
    course.allow_skipping = data.get('allow_skipping', course.allow_skipping)
    course.sign_off_required = data.get('sign_off_required', course.sign_off_required)
    if 'expires_on' in data and data['expires_on']:
        course.expires_on = datetime.datetime.strptime(data['expires_on'], '%Y-%m-%d')
    course.language = data.get('language', course.language)

    course.groups_can_be_assigned_to.clear()

    course.save()
    for group_id in data['groups_ids']:
        if group_id=='-2':
            for group in auth_models.Group.objects.all():
                cb_list = CourseGroupCanBeAssignedTo.objects.filter(course=course, group=group)
                if not cb_list:
                    cb = CourseGroupCanBeAssignedTo(course=course, group=group)
                else:
                    cb = cb_list[0]
                    for course_cba in cb_list[1:]:
                        course_cba.delete()
                cb.save()
        else:
            CourseGroupCanBeAssignedTo(course=course, group=auth_models.Group.objects.get(id=group_id)).save()

    return HttpJsonOkResponse()
        

@decorators.is_admin_or_superadmin
def assign_module(request):

    if request.user.get_profile().is_admin:
        groups = request.user.groups.all().order_by('name')
        users = auth_models.User.objects.filter(groups__in=groups).distinct()
    else:
        groups = auth_models.Group.objects.all().order_by('name')
        users = auth_models.User.objects.all()

    return render(request, 'content/module_assignment.html', {
        'form': forms.SearchAssignmentsForm(initial={'owner': request.user}),
        'groups': groups,
        'users': users,
        'settings': {'SALES_PLUS': settings.SALES_PLUS}
         })

@http_decorators.require_POST    
def preview_assignment(request):
    data = json.loads(request.raw_post_data)
    parsed_modules_list = ''
    templates = [ MailTemplate.MSG_IDENT_ADD_MULTI_ASSIGNMENTS,
                  MailTemplate.MSG_IDENT_ADD_ASSIGNMENT,
                  MailTemplate.MSG_IDENT_ADD_ASSIGNMENT_OCL ]
    
    group = data.get('group', False)
    modules = data.get('modules')
    ocl_enabled = data.get('ocl_enabled')
    
    if data.get('savedTemplate'):
        template = data.get('savedTemplate').get('content')
        templateType = data.get('savedTemplate').get('type')
    else:
        template = MailTemplate.for_user(request.user,
                    identifier=templates[(lambda: 0 if len(modules) > 1 else (lambda: 1 if ocl_enabled else 2)())()])[0]
        template = template.content
    
    if modules:
        i = 0
        for key in modules.keys():
            i+=1
            if ocl_enabled:
                ocl = MailTemplate.ONE_CLICK_LINK_SMM % (request.get_host(), int(key), '(ocl_token)')
                if not settings.SALES_PLUS:
                    ocl = MailTemplate.ONE_CLICK_LINK % (request.get_host(), '(ocl_token)')
                parsed_modules_list += '%d. "%s"<br />%s<br>' % (i, modules[key], ocl,)
            else: 
                parsed_modules_list += '%d. "%s"<br />' % (i, modules[key],)

    filledTemplate = template.replace('[groupname]', group)            
    if len(modules) > 1:
        filledTemplate = filledTemplate.replace('[moduleslist]', parsed_modules_list)
    elif len(modules) == 1:
        filledTemplate = filledTemplate.replace('[moduletitle]', modules.values()[0])
    
    return render(request, 'content/dialogs/preview_assignment.html',
                              {'notificationBody': filledTemplate}) 

@decorators.is_admin_or_superadmin
def create_module(request, id=None):
    """Displays rendering of the module creator screen.

    :param request: Request.
    :param id: Optional ID of the module to be re-edited.
    """

    ctx = {
        'form': forms.FileFindForm(),
    }
    if id is not None:
        ctx['course'] = get_object_or_404(models.Course, pk=id)
    return render(request, 'content/module_creator.html', ctx)


@decorators.is_admin_or_superadmin
def copy_module(request, id):
    """Creates copy of module from existing module.

    :param request: Request.
    :param id: Identifier of module to create copy from.
    """
    base_module = get_object_or_404(models.Course, pk=id)
    new_module = deepcopy(base_module)
    new_module.title += ' Copy'
    new_module.id = None
    new_module.state_code = Draft.CODE
    new_module.save()

    for old_segment in base_module.segment_set.all():
        new_segment = deepcopy(old_segment)
        new_segment.course = new_module
        new_segment.id = None
        new_segment.save()

    return redirect('content-edit_module', id=new_module.id)

@decorators.login_or_token_required
def view_module_smm(request, id=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('content-view_module', kwargs={'id': id}))

    token = request.GET.get('token')
    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        if id is not None:
            course = get_object_or_404(models.Course, pk=id)
            if not course.is_available_for_user(one_click_link_token.user):
                raise Http403()
                return render_to_response()
        
        ctx = {'course': course,
               'token': token,
               'allow_login': one_click_link_token.allow_login and \
                              not one_click_link_token.user.get_profile().is_user_plus}
        
        user = one_click_link_token.user
            
        show_sign_off_button = False
        if module_with_track_ratio(one_click_link_token.user.id, course.id) == 1 and\
                course.sign_off_required:
            try:
                course_user = CourseUser.objects.get(course=course,
                                                     user=user)
            except CourseUser.DoesNotExist:
                show_sign_off_button = True
        
        ctx['show_sign_off_button'] = _show_sign_off_button(user, course)
        return render(request, 'content/module_viewer_smm.html', ctx)

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
    return render(request, 'content/module_viewer.html', ctx)


@decorators.login_or_token_required
def sign_off_module(request, id):
    course = get_object_or_404(models.Course, pk=id)
    
    token = request.GET.get('token')
    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return bls_django.HttpJsonResponse({'status': 'ERROR',
                   'error': unicode(_('User is not allowed to view this content.'))})
            
    if request.user.is_authenticated():
        user = request.user
    else:
        user = one_click_link_token.user
    
    if not course.is_available_for_user(user):
        return bls_django.HttpJsonResponse({'status': 'ERROR',
            'error': unicode(_('User is not allowed to view this content.'))})

    if course.sign_off_required:
        if module_with_track_ratio(user.id, course.id) == 1:
            try:
                course_user = CourseUser.objects.get(course=course,
                        user=user)
            except CourseUser.DoesNotExist:
                 course_user = CourseUser(course=course,
                        user=user)
            course_user.sign_off = True
            course_user.sign_off_date = datetime.datetime.now()
            course_user.save()
        else:
            return bls_django.HttpJsonResponse({'status': 'ERROR',
                    'error': unicode(_('Module is not finished yet.'))})
    else:
        return bls_django.HttpJsonResponse({'status': 'ERROR',
                'error': unicode(_('Module does not have sign off option'))})

    return bls_django.HttpJsonOkResponse()


@decorators.login_or_token_required
def show_sign_off_button(request, id):
    course = get_object_or_404(models.Course, pk=id)
    token = request.GET.get('token')
    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return bls_django.HttpJsonResponse({'status': 'ERROR',
                   'error': unicode(_('User is not allowed to view this content.'))})
            
    if request.user.is_authenticated():
        user = request.user
    else:
        user = one_click_link_token.user
        
    if not course.is_available_for_user(user):
        return bls_django.HttpJsonResponse({'status': 'ERROR',
            'error': unicode(_('User is not allowed to view this content.'))})
    
    show_button = _show_sign_off_button(user, course)
    return bls_django.HttpJsonResponse({"status": "OK", "show": show_button})


@decorators.is_admin_or_superadmin
def find_files(request):
    """Handles files search based on various criteria.

    :param request: Request.

    Optional GET parameters:
        - ``page`` -- Page to be displayed. Expected values are positive
          integers. Page 1 is the oldest one. Entries are sorted in ascending
          order, by date of creation. If this parameter is omitted, most
          recent entries will be returned.
        - ``tags_ids`` -- Tag strings separated with ","
        - ``file_name`` -- Part of the filename.
        - ``language`` -- Id of language for which files should be searched - 0
            if all languages are accepted.
        - ``file_type`` -- Id of file type for which files should be searched - 0
            if no file type specified.

    Return values:
        - 200 response with entries encoded as a JSON object.
        - 404 response is returned if the ``page`` parameter has incorrect
          value or attempts to address inexisting page.
    """

    n = request.GET.get('page')
    if n is not None:
        try:
            n = int(n)
        except ValueError:
            return http.HttpResponseNotFound('Requested page was not found.')

    tags_ids = request.GET.get('tags_ids', '')
    language = request.GET.get('language', '')
    file_name = request.GET.get('file_name', '')
    file_type = request.GET.get('file_type', '')
    my_files = request.GET.get('my_files', '')
    inactive_files = request.GET.get('inactive_files', '')

    if request.user.get_profile().is_superadmin:
        from_my_groups = request.GET.get('from_my_groups', '')
    else:
        from_my_groups = "1"
    
    files = models.File.objects.filter(is_removed=False)
    if tags_ids:
        for tag in tags_ids.split(","):
            files = files.filter(tag__name__iexact=tag)

    if language:
        files = files.filter(language=language)
    if file_name:
        files = files.filter(title__icontains=file_name)
    if file_type:
        files = files.filter(type=file_type)
    if my_files == '1':
        files = files.filter(owner=request.user)
    else:
        if (request.user.get_profile().is_superadmin and from_my_groups == '1') or request.user.get_profile().is_admin:
            files = files.filter(Q(groups__in=request.user.groups.values_list('id', flat=True))|Q(owner=request.user)).distinct()

    if inactive_files == "1":
        files = files.filter(status__in=(File.STATUS_AVAILABLE,
                                         File.STATUS_EXPIRED))
    else:
        files = files.filter(status=File.STATUS_AVAILABLE)

    if not tags_ids and not language and not file_name and not file_type :
        files = files.all()

    p = paginator.Paginator(files, settings.CONTENT_PAGE_SIZE)

    # If no page has been specified, return last page (most recent).
    if n is None:
        n = p.num_pages

    try:
        page = p.page(n)
    except (paginator.EmptyPage, paginator.InvalidPage):
        return http.HttpResponseNotFound('Requested page was not found.')

    elements = list(page.object_list)
    # If the most recent page isn't full, then add there few elements from the
    # second to last page. Unless we have only one page.
    # TODO: Clean this up.
    if (len(elements) < settings.CONTENT_PAGE_SIZE) and (n == p.num_pages > 1):
        missing_count = settings.CONTENT_PAGE_SIZE - len(elements)
        extra = list(p.page(n - 1).object_list)[-missing_count:]
        extra.extend(elements)
        elements = extra
        
    entries = []
    for file in elements:
        taglist = []
        grouplist = []
        for t in file.tag_set.all():
            taglist.append([t.name, tagging_models.get_tag_label(t.type)])
        for group in file.groups.all():
            grouplist.append(group.name)
        usage_query = Course.objects.filter(id__in=(Segment.objects.filter(file=file).values_list('course__id')))
        usage = usage_query.count() or '0'
        usage_active = usage_query.filter(state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).count() or '0'
        expires_on = file.expires_on
        owner = 'unknown'
        if file.owner:
            owner = file.owner.first_name + " " + file.owner.last_name
        if expires_on:
            expires_on = serializers.date_to_unix(expires_on)

        entries.append({
            'id': file.id,
            'title': conditional_escape(file.title),
            'type': file.type,
            'created_on': serializers.ts_to_unix(file.created_on),
            'expires_on': expires_on,
            'url': file.view_url,
            'language': _get_language_name(file.language),
            'owner': owner,
            'allow_downloading': ugettext("Yes") if file.is_downloadable else ugettext("No"),
            'note': file.note or '',
            'tags': taglist,
            'groups': grouplist,
            'thumbnail_url': file.thumbnail_url,
            'duration': file.duration,
            'is_removable': not _is_file_in_use_in_active_course(file.id) or request.user.get_profile().role == manage_models.UserProfile.ROLE_SUPERADMIN,
            'usage': usage,
            'usage_active': usage_active,
            'is_editable': request.user.get_profile().is_superadmin or file.owner == request.user,
            'is_removable': request.user.get_profile().is_superadmin or (file.owner == request.user and not _is_file_in_use_in_active_course(file.id)),
            'pages_num': file.pages_num
            })
        
            # the above structure is missing 2 fields: allowScaling and duration
    entries.reverse()

    response = {
        'meta': {
            'curr-page-url': urlresolvers.reverse(find_files) + '?page=%d&tags_ids=%s&language=%s&file_name=%s&file_type=%s&my_files=%s&inactive_files=%s&from_my_groups=%s' % (n, tags_ids, language, file_name, file_type, my_files, inactive_files, from_my_groups),
            'curr-page': n,
            'total-pages': p.num_pages,
            'total-entries': len(files)
            },
        'entries': entries,
        }

    if n > 1:
        response['meta']['prev-page-url'] = urlresolvers.reverse(find_files) + '?page=%d&tags_ids=%s&language=%s&file_name=%s&file_type=%s&my_files=%s&inactive_files=%s&from_my_groups=%s' % (n - 1, tags_ids, language, file_name, file_type, my_files, inactive_files, from_my_groups)

    if n < p.num_pages:
        response['meta']['next-page-url'] = urlresolvers.reverse(find_files) + '?page=%d&tags_ids=%s&language=%s&file_name=%s&file_type=%s&my_files=%s&inactive_files=%s&from_my_groups=%s' % (n + 1, tags_ids, language, file_name, file_type, my_files, inactive_files, from_my_groups)

    return bls_django.HttpJsonResponse(response)


@auth_decorators.login_required
@http_decorators.require_GET
def edit_content(request, file_id):

    file = models.File.objects.get(id=file_id)

    # Checking if user has rights to edit content.
    # Only content owner and superadmin is permitted.
    if not request.user.get_profile().is_superadmin and file.owner.id != request.user.id:
        return http.HttpResponseBadRequest('User is not permitted to edit this content.')

    selectedGroups = file.groups.all()
    availableGroups = [val for val in auth_models.Group.objects.all() if val not in selectedGroups]

    return render(request, 'content/module_content.html',
                               {'is_edited': True,
                                'importFileForm': forms.FileImportForm(),
                                'orig_filename': file.orig_filename,
                                'tags': file.tag_set.all(),
                                'availableGroups': availableGroups,
                                'selectedGroups': selectedGroups,
                                'file_type': file.type,
                                'is_duration_visible': not file.type in [File.TYPE_AUDIO, File.TYPE_VIDEO],
                                'manageContentForm': forms.ManageContentForm(initial={
                                    'title': file.title,
                                    'file_id': file.id,
                                    'owner': file.owner,
                                    'delete_expired': file.delete_expired,
                                    'expires_on': file.expires_on or '',
                                    'note': file.note,
                                    'language': file.language,
                                    'is_downloadable': file.is_downloadable,
                                    'duration': file.duration,
                                })})

@http_decorators.require_POST
@decorators.is_admin_or_superadmin
def save_manage_content(request):

    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')
    if data['owner']:
        file_owner_id = data['owner']
    else:
        file_owner_id = request.user.id
    
    file = models.File.objects.get(id=data['file_id'])
    file.title = data['title']
    if data['expires_on']:
        file.expires_on = datetime.datetime.strptime(data['expires_on'], '%Y-%m-%d')
    else:
        file.expires_on = None
    file.note = data['note']
    file.language = data['language']
    file.owner = auth_models.User.objects.get(id=file_owner_id)
    file.delete_expired = data['delete_after_expire']
    file.is_downloadable = data['is_downloadable']

    if(not file.type in [File.TYPE_AUDIO, File.TYPE_VIDEO]):
        file.duration = data['duration']

    file.tag_set.clear()
    file.tag_set.add(add_if_not_exist(file.owner.first_name + " " + file.owner.last_name, is_default=True, type=tagging_models.TYPE_OWNER))
    file.groups.clear()
    for group_id in data['selected_groups_ids']:
        g = auth_models.Group.objects.get(id=group_id)
        file.groups.add(g)
        g.groupprofile.save()
        file.tag_set.add(add_if_not_exist(auth_models.Group.objects.get(id=group_id).name, is_default=True, type=tagging_models.TYPE_GROUP))

    bind_tags_with_file(file, data['tags_ids'], data['new_tags_names'])
    file.save()

    if file.status == File.STATUS_UPLOADED:
        tasks.process_stored_file.delay(file)

    return bls_django.HttpJsonOkResponse()

def _is_file_in_use_in_active_course(file_id):
    return Segment.objects.filter(Q(course__state_code=Active.CODE) |
                                  Q(course__state_code=ActiveAssign.CODE) |
                                  Q(course__state_code=ActiveInUse.CODE)).filter(file__id=file_id).count() > 0

@http_decorators.require_POST
@decorators.is_admin_or_superadmin
def delete_content(request, file_id):
    file = get_object_or_404(File, id=file_id)

    if request.user.get_profile().is_admin and file.owner != request.user:
        return http.HttpResponseBadRequest('Admin can remove only his files.')

    if request.user.get_profile().is_admin and _is_file_in_use_in_active_course(file_id):
        return http.HttpResponseBadRequest('Admin cant remove files which are in use by active courses.')

    _remove_file_if_exists(settings.CONTENT_UPLOADED_DIR, file.orig_file_path)
    
    if file.type == File.TYPE_AUDIO:
        for fileFormat in ConfigEntry.CONTENT_AUDIO_FORMATS:
            filePath, fileExt = os.path.splitext(file.conv_file_path)
            _remove_file_if_exists(settings.CONTENT_AVAILABLE_DIR, ''.join([filePath,'.',fileFormat]))
    elif file.type == File.TYPE_VIDEO:
        for fileFormat in ConfigEntry.CONTENT_VIDEO_FORMATS:
            filePath, fileExt = os.path.splitext(file.conv_file_path)
            _remove_file_if_exists(settings.CONTENT_AVAILABLE_DIR, ''.join([filePath,'.',fileFormat]))
    else: 
        _remove_file_if_exists(settings.CONTENT_AVAILABLE_DIR, file.conv_file_path)
        
    _remove_file_if_exists(settings.CONTENT_THUMBNAILS_DIR, file.thumbnail_file_path)

    if Segment.objects.filter(file__id=file_id).count() > 0:
        file.status = File.STATUS_REMOVED
        file.save()
    else:
        file.delete()
        
    return bls_django.HttpJsonOkResponse()

def _remove_file_if_exists(dir_path, file_path):
    full_path = os.path.join(settings.MEDIA_ROOT, dir_path, file_path)
    if os.path.isfile(full_path):
        os.remove(full_path)

@decorators.is_admin_or_superadmin
def files_manage(request):
    ctx = {
        'form': forms.FileFindForm(),
        }
    return render(request, 'content/files_manage.html', ctx)

@decorators.is_admin_or_superadmin
def import_file(request):
    """Handles file import.

    :param request: Request.

    This view can be access with either GET or POST. If request is of type
    GET, an upload form will be displayed.

    POST request is used for file upload. Fields required in the POST request:
        - ``title`` -- Title to be assigned to the file.
        - ``file`` -- multipart/form-data encoded file which is being
          uploaded.

    WARNING! Method supposes that when form is not valid,
    then maximum file upload size is reached. Check out FILE_UPLOAD_HANDLERS
    - if no handler consume file, django dont fill form.file field.

    Response:
        - For a POST request, response code is 200 if a validation
          error occurs, body cotains HTML. Upon successful upload response
          code is 302 (temporary redirect) to an URL with information about
          completed upload.
    """
    if request.method == 'GET':
        selectedGroups = request.user.groups.all()
        availableGroups = [val for val in auth_models.Group.objects.all() if val not in selectedGroups]

        return render(request, 'content/module_content.html', {'importFileForm': forms.FileImportForm(),
                                                                           'manageContentForm': forms.ManageContentForm(initial={'owner': request.user.pk}),
                                                                           'availableGroups': availableGroups,
                                                                           'selectedGroups': selectedGroups,
                                                                           'dms_enabled': get_entry_val(ConfigEntry.CONTENT_USE_DMS) == "True",
                                                                           'user_id': request.user.id})

    form = forms.FileImportForm(request.POST, request.FILES)
    if form.is_valid():
        def coping_file_callback(full_orig_file_path):
            with closing(storage.default_storage.open(full_orig_file_path, 'wb')) as fh:
                for chunk in form.cleaned_data['file'].chunks():
                    fh.write(chunk)

        return _save_imported_file(request.user, form.cleaned_data['file'].name, coping_file_callback)

    return http.HttpResponse("{\"status\": \"ERROR\", \"message\": \"%s\"}" % unicode(_("Exceeded maximum file upload size.")))

def _save_imported_file(user, orig_filename, coping_file_callback):
        if not File.is_supported_file(orig_filename):
            return http.HttpResponse("{\"status\": \"ERROR\", \"message\": \"%s\"}" %  unicode(_("Unsupported file type.")))

        file = models.File(
        #    type = models.File.type_from_name(orig_filename),
            orig_filename = orig_filename)

        full_orig_file_path = os.path.join(settings.CONTENT_UPLOADED_DIR, file.orig_file_path)
        coping_file_callback(full_orig_file_path)


        try:
            file.type = models.File.type_from_name(full_orig_file_path)
        except utils.UnsupportedFileTypeError:
            return http.HttpResponse("{\"status\": \"ERROR\", \"message\": \"%s\"}" %  unicode(_("Unsupported file type.")))

        file.save()
        file.tag_set.add(add_if_not_exist(user.username, is_default=True))
        file.save()

        if file.type == models.File.TYPE_IMAGE:
            lang = ''
        else:
            lang = user.get_profile().language

        is_duration_visible = not file.type in [File.TYPE_AUDIO, File.TYPE_VIDEO]
        return http.HttpResponse("""{"status": "OK", \
                                    "file_id":"%s", \
                                    "file_orig_filename": "%s", \
                                    "selected_language":"%s", \
                                    "file_type": "%s", \
                                    "is_duration_visible": "%s"}""" % (str(file.id), file.orig_filename,
                                                                       lang, str(file.type), is_duration_visible))

# TODO: We are not using CSRF protection on this one. It is bad and needs to
#       be fixed.
@csrf_exempt
@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def save_module(request):
    """Updates or creates new module.
    """

    response = {
        'version': 1,
        'meta': {},
        }
    p = models.ModuleDescrParser(request.raw_post_data, request.user)
    try:
        id = p.parse()
        response['meta']['id'] = id
    except models.ModuleDescrError, e:
        response['errors'] = [{
                'field': e.field,
                'message': str(e),
            }]

    return bls_django.HttpJsonResponse(response)

def _active_modules():
    return models.Course.objects.filter(Q(state_code=Active.CODE) |
                                           Q(state_code=ActiveAssign.CODE) |
                                           Q(state_code=ActiveInUse.CODE)).order_by('-published_on')
@decorators.is_admin_or_superadmin
def modules_list(request):
    
    drafts = models.Course.objects.filter(state_code=Draft.CODE).order_by('-updated_on')
    active = _active_modules()
    inactive = models.Course.objects.filter(Q(state_code=Deactivated.CODE) |
                                            Q(state_code=DeactivatedUsed.CODE)).order_by('-deactivated_on')

    if request.user.get_profile().is_admin:
        drafts = drafts.filter(owner=request.user)
        active = active.filter(owner=request.user)
        inactive = inactive.filter(owner=request.user)

    courses_dict = []
    for course in list(drafts) + list(active) + list(inactive):
        courses_dict.append(serializers.serialize_course(course, request.user, TrackingEventService()))
    return bls_django.HttpJsonResponse(courses_dict)

@decorators.is_admin_or_superadmin
def active_modules_list(request):
    show_my_modules = request.GET.get('my', '0')
    active_modules = _active_modules()
    if request.user.get_profile().is_admin and show_my_modules == '1':
        active_modules = active_modules.filter(owner=request.user)
    elif request.user.get_profile().is_admin and show_my_modules == '0':
        active_modules = active_modules.filter(groups_can_be_assigned_to__in=request.user.groups.values_list('id', flat=True)).exclude(owner=request.user).distinct()
        
    courses = []
    for course in active_modules:
        course_data = serializers.serialize_course(course, request.user, TrackingEventService())
        course_data['meta']['owner']=' '.join((course.owner.first_name,course.owner.last_name))
        courses.append(course_data)
            
    return bls_django.HttpJsonResponse(courses)

#
# TODO: If a normal user requests a module descr then we should check if it is
#       assigned to him.
#
@decorators.login_or_token_required
@http_decorators.require_GET
def module_descr(request, id):
    """Creates module description.
    """

    course = get_object_or_404(models.Course, pk=id)

    user = request.user
    format = request.GET.get('format', 'json')
    token = request.GET.get('token')
    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        
        if one_click_link_token.expired:
            return render(request,
                    'registration/login.html', {"ocl_expired": True})

        if not course.is_available_for_user(one_click_link_token.user):
            raise Http403
            return render_to_response()
        user = one_click_link_token.user

    if not settings.SALES_PLUS:
        course.completion_msg = ''

        
    if format == 'json':
        return bls_django.HttpJsonResponse(serializers.serialize_course(
                course, user, TrackingEventService(), ocl_token=token))
    elif format == 'xml':
        return http.HttpResponse(serializers.serialize_course_xml(
                course, user), mimetype='application/xml')
    return http.HttpResponseNotFound('Requested module not found.')

def files_number(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)

    files = []
    if report.user_id:
        files = File.objects.filter(owner=report.user_id, status=File.STATUS_AVAILABLE)
    elif report.admin_id:
        files = File.objects.filter(owner=report.admin_id, status=File.STATUS_AVAILABLE)
    elif report.group_id:
        files = File.objects.filter(groups__id__contains=report.group_id,
                                    groups__id__in=owner_groups,
                                    status=File.STATUS_AVAILABLE)
    
    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    if request.GET.get('show_header', ''):
        columns = ['']
        for file_type in File.TYPES:
            columns.append(unicode(file_type[1]))
        writer.writerow(columns)

    admin_files = {}
    for file in files:
        admin_files[file.owner] = {}
        for type, value in File.TYPES:
            admin_files[file.owner].setdefault(type, 0) 
    
    for file in files:
        admin_files[file.owner][file.type] += 1

    for admin_file in admin_files:
        if admin_file != None:
            columns = [admin_file.first_name + ' ' + admin_file.last_name]
            for type, value in File.TYPES:
                columns.append(str(admin_files[admin_file][type]))
            writer.writerow(columns)
    
    return reports.get_csv('files_number.csv', result)

def dropped_files(request):
    return


@http_decorators.require_GET
@decorators.is_admin_or_superadmin
def list_collections(request):
    collections = models.Collection.objects.filter(owner=request.user)
    json_collections = [serializers.serialize_collection(col) for col in collections]

    return bls_django.HttpJsonResponse(json_collections)

@http_decorators.require_POST
@decorators.is_admin_or_superadmin
def create_collection(request):
    data = json.loads(request.raw_post_data)
    collection = create_collection_from_data(data=data, user=request.user)
    return bls_django.HttpJsonResponse({'id': collection.id})

@http_decorators.require_POST
@decorators.is_admin_or_superadmin
def save_collection(request, id):
    data = json.loads(request.raw_post_data)
    collection = get_object_or_404(models.Collection, pk=id)
    
    # Checking if user has rights to save collection.
    # Only collection owner and superadmin is permitted.
    if not request.user.get_profile().is_superadmin and collection.owner.id != request.user.id:
        return http.HttpResponseBadRequest('User is not permitted to edit this content.')

    create_collection_from_data(data=data, user=request.user, collection=collection)

    return bls_django.HttpJsonOkResponse()

@http_decorators.require_POST
@decorators.is_admin_or_superadmin
def delete_collection(request, id):
    collection = get_object_or_404(models.Collection, pk=id)

    # Checking if user has rights to delete collection.
    # Only collection owner and superadmin is permitted.
    if not request.user.get_profile().is_superadmin and collection.owner.id != request.user.id:
        return http.HttpResponseBadRequest('User is not permitted to edit this content.')

    collection.delete()

    return bls_django.HttpJsonOkResponse()

def create_collection_from_data(data, user, collection=None):
    if not collection:
        collection = models.Collection(owner=user)
    collection.name = data['meta']['title']
    models.CollectionElem.objects.filter(collection=collection).delete()
    collection.collectionelem_set.all().delete()
    collection.save()
    for pos, file_id in enumerate(data['track0']):
        f = models.File.objects.get(pk=file_id)
        models.CollectionElem(collection=collection,
                              file=f,
                              position=pos).save()
    collection.save()
    return collection


@http_decorators.require_POST
@decorators.is_admin_or_superadmin
def change_state(request, id):
    course = get_object_or_404(models.Course, pk=id)
    data = json.loads(request.raw_post_data)
    try:
        errors = course.get_state().act(data["new_state"])
        if errors:
            return bls_django.HttpJsonResponse({'status': 'ERROR', 'messages': errors})
        else:
            return bls_django.HttpJsonOkResponse()
    except InvalidActionError, e:
        return http.HttpResponseBadRequest(str(e))

@decorators.is_admin_or_superadmin
def choose_file_from_dms(request):
    if request.method == 'GET':
        return render(request, 'content/dialogs/choose_file_from_dms.html')
    else:
        dms_path = get_entry_val(ConfigEntry.CONTENT_DMS_PATH)
        data = json.loads(request.raw_post_data)

        def coping_file_callback(full_orig_file_path):
            full_url = os.path.join(dms_path, data['file_path']).encode("utf-8")
            f = open(full_url)
            file_from_dms = django.core.files.File(f)
            storage.default_storage.save(full_orig_file_path, file_from_dms)
            f.close()

        return _save_imported_file(request.user, data['file_name'], coping_file_callback)

@http_decorators.require_GET
@decorators.is_admin_or_superadmin
def dms_files(request):
    if get_entry_val(ConfigEntry.CONTENT_USE_DMS) == "False":
        return http.HttpResponseBadRequest("Dms is disabled.")

    dms_path = get_entry_val(ConfigEntry.CONTENT_DMS_PATH)
    if request.GET['root'] != 'source':
        base = request.GET['root']
    else:
        base = ''

    try:
        result = []
        for fname in _sorted_listdir(os.path.join(dms_path, base).encode("utf-8")): 
            if os.path.isdir(os.path.join(dms_path, base, fname).encode("utf-8")):
                result.append({
                    "id": os.path.join(base, fname),
                    "text": fname,
                    "hasChildren": True,
                    "classes": "folder"
                })
            else:
                result.append({
                    "id": os.path.join(base, fname),
                    "text": fname,
                    "classes": "file"
                })
    except Exception, e:
        return HttpResponseServerError(str(e))
    
    return HttpJsonResponse(result)

def _sorted_listdir(path):
    list = os.listdir(path)
    list = [elem.decode("utf-8") for elem in list]
    list.sort(cmp)
    return list

''' please check it due to possible vulnerablity! '''
def file_source(request, id):
    file = ""
    fh = open(os.path.join(settings.MEDIA_ROOT, settings.CONTENT_AVAILABLE_DIR, id) + '.txt')
    for line in fh:
        file += line + "\n"
    ctx = {
           'f': file
    }
    return render(request, 'content/file_source.html', ctx)

def load_by_segment(request, id):
    
    file = get_object_or_404(models.File, pk=id)
 
    taglist = []
    grouplist = []
    for t in file.tag_set.all():
        taglist.append(t.name)
    for group in file.groups.all():
        grouplist.append(group.name)
    usage_query = Course.objects.filter(id__in=(Segment.objects.filter(file=file).values_list('course__id')))
    usage = usage_query.count() or '0'
    usage_active = usage_query.filter(state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).count() or '0'
    expires_on = file.expires_on
    owner = 'unknown'
    if file.owner:
        owner = file.owner.first_name + " " + file.owner.last_name
    if expires_on:
        expires_on = serializers.date_to_unix(expires_on)

    json = {
        'id': file.id,
        'title': conditional_escape(file.title),
        'type': file.type,
        'created_on': serializers.ts_to_unix(file.created_on),
        'expires_on': expires_on,
        'url': file.view_url,
        'language': _get_language_name(file.language),
        'owner': owner,
        'allow_downloading': ugettext("Yes") if file.is_downloadable else ugettext("No"),
        'note': file.note or '',
        'tags': taglist,
        'groups': grouplist,
        'thumbnail_url': file.thumbnail_url,
        'duration': file.duration,
        'is_removable': not _is_file_in_use_in_active_course(file.id) or request.user.get_profile().role == manage_models.UserProfile.ROLE_SUPERADMIN,
        'usage': usage,
        'usage_active': usage_active,
        'is_editable': request.user.get_profile().is_superadmin or file.owner == request.user,
        'is_removable': request.user.get_profile().is_superadmin or (file.owner == request.user and not _is_file_in_use_in_active_course(file.id)),
        'pages_num': file.pages_num
        }

    return HttpJsonResponse(json)


def download_segment(request, segment_id):
    token = request.GET.get('token')
    user = request.user

    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        
        if one_click_link_token.expired:
            return render(request,
                    'registration/login.html', {"ocl_expired": True})
        if not user.is_authenticated():
            user = one_click_link_token.user

    segment = get_object_or_404(Segment, id=segment_id)
    if not segment.file.is_downloadable:
        return HttpResponse(status=403, content="File is not downloadable")
    DownloadEvent.objects.create(segment=segment, user=user)
    
    return _download_file(segment.file)

def download_file(request, file_id):
    return _download_file(get_object_or_404(File, id=file_id))

def _download_file(file):
    file_path = storage.default_storage.path(os.path.join(settings.CONTENT_UPLOADED_DIR, file.orig_file_path))
    src_file = open(file_path, 'r')

    response = http.HttpResponse(FileWrapper(src_file), content_type=mimetypes.guess_type(file.orig_filename))
    response['Content-Disposition'] = "attachment; filename=\"%s\"" % file.orig_filename.encode("utf-8")
    response['Content-Length'] = os.path.getsize(file_path)
    return response

def _show_sign_off_button(user, course):
    if course.sign_off_required:
        if module_with_track_ratio(user.id, course.id) == 1:
            try:
                course_user = CourseUser.objects.get(course=course,
                        user=user)
                if not course_user.sign_off:
                    return True
            except CourseUser.DoesNotExist:
                return True

    return False

@decorators.is_admin_or_superadmin
def rss_feeds_list(request):
    return render(request, 'content/rss.html', {
        'groups': auth_models.Group.objects.all()})


class AssignedModulesFeed(Feed):
    """RSS feed with modules assigned to a group.
"""

    link = '/'

    def get_object(self, request, group_id):
        return get_object_or_404(auth_models.Group, id=group_id)

    def title(self, group):
        return _('Modules assigned to %(group_name)s') % {
            'group_name': group.name}

    def items(self, group):
        active_states = [Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE]
        return Course.objects.filter(
            groups__in=[group],
            state_code__in=active_states)

    def item_title(self, course):
        return course.title

    def item_description(self, course):
        return course.objective

    def item_link(self, course):
        return urlresolvers.reverse(view_module, kwargs={'id': course.id})

    def item_pubdate(self, course):
        # In case the publish action doesn't set Course.published_on attribute
        # fallback to current date. In the future Course model should be fixed
        # to encapsulate all logic of the publish action so that the proper
        # behaviour can be verified more quickly.
        date = course.published_on
        if date is None:
            date = datetime.datetime.now()
        return date

# vim: set et sw=4 ts=4 sts=4 tw=78:
