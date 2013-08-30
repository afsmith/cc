# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#     Bartosz Oler <bartosz.oler@blstream.com>
#
#

"""Django views.
"""

import codecs
import csv
import cStringIO as StringIO
import json
import os

from django.contrib.auth import authenticate
from django.forms.fields import CharField
from django.views.decorators.csrf import csrf_exempt
import ldap

from django import http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, SiteProfileNotAvailable
from django.contrib.auth.views import login, redirect_to_login
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as db_models, transaction
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django_auth_ldap.backend import LDAPBackend, _LDAPUser, LDAPSettings
from django.utils import translation
from django.utils.translation import ugettext as _
from longerusername.forms import AuthenticationForm
from bls_common.bls_django import HttpJsonOkResponse, HttpJsonResponse
from cc.apps.content.course_states import ActiveInUse, DeactivatedUsed, Active, ActiveAssign

from cc.apps.content.models import Collection, Course, CourseGroup, File

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators import http as http_decorators
from django.shortcuts import render

#from administration import models as admin_models
#from administration.models import ConfigEntry
from bls_common import bls_django
from messages.models import Message
from management.models import OneClickLinkToken
#from messages_custom.models import MailTemplate
#from messages_custom.utils import send_email, send_message
from plato_common import decorators
from management import forms, models
#from reports.models import Report
from tracking.models import TrackingEvent
#from reports import reports


@decorators.is_admin_or_superadmin
def users(request):
    """Displays main users management panel.

    :param request: Request.
    """
    ctx = {
        "settings": {
            "REGISTRATION_OPEN": settings.REGISTRATION_OPEN
        }
    }
    ctx["tabname"] = 'groups_users'
    return render(request, 'management/users.html', ctx)


@decorators.is_admin_or_superadmin
def user_form_validator(request):
    """ validate user form """
    if request.method == 'POST':
        form = forms.UserProfileForm(request.POST, admin=request.user)
    if not form.is_valid():
        if len(form.errors)==1 and 'group' in form.errors.keys():
            ctx = {'id': -1}
            response = bls_django.HttpJsonResponse(ctx)
            response.status_code = 201
            return response
    ctx = {
        'form': form,
        'type' : 'pending',
        }
    return render(request, 'management/dialogs/edit_user.html', ctx)

@decorators.is_admin_or_superadmin
def create_user(request):
    """Handles user creation.

    :param request: Request.

    Return values:
    - 200 if user is requesting the form (GET) or if validation
      errors occured.
    - 201 if user was created successfully.
    """

    if request.method == 'POST':
        form = forms.UserProfileForm(request.POST, admin=request.user)
        if form.is_valid():
            password = User.objects.make_random_password()
            role = form.cleaned_data['role']

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=password)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            g = form.cleaned_data['group']
            user.groups.add(g)
            g.groupprofile.save()

            profile = models.UserProfile(
                user=user,
                phone=form.cleaned_data['phone'],
                #language=form.cleaned_data['language'],
                role=role)
            profile.save()

            if role == models.UserProfile.ROLE_ADMIN:
                # TODO: Test if current user can assign users to the given
                #       group.
                group_profile = models.UserGroupProfile(
                    user=user, group=form.cleaned_data['group'])
                group_profile.save()

            if form.cleaned_data['ocl']:
                ocl = OneClickLinkToken.objects.create(user=user)
                send_email(recipient=user, user=request.user,
                           msg_ident=MailTemplate.MSG_IDENT_WELCOME_OCL,
                           msg_data={"[username]": user.username,
                                     "[password]": password,
                                     "[oneclicklink]":
                                     MailTemplate.ONE_CLICK_LINK %
                                     (request.get_host(), ocl.token)},
                           ocl=ocl)
            else:
                send_email(recipient=user, user=request.user,
                           msg_ident=MailTemplate.MSG_IDENT_WELCOME,
                           msg_data={"[username]":user.username,
                                     "[password]":password})

            ctx = {
                'id': user.id,
            }
            response = bls_django.HttpJsonResponse(ctx)
            response.status_code = 201

            return response
    else:
        initial = {
            'role' : models.UserProfile.ROLE_USER,
        }
        form = forms.UserProfileForm(initial=initial, admin=request.user)
    ctx = {
        'form': form,
        'type' : request.GET.get('type', 'now'),
        }
    return render(request, 'management/dialogs/edit_user.html', ctx)


@decorators.is_admin_or_superadmin
def edit_user(request, id):
    """Handles user editing.

    :param request: Request.
    :param id: Identifier, from the database, of the user to edit.

    Return values:
    - 200 if user is requesting the form (GET request), or if there are
      validation errors (POST request).
    - 201 if everything is OK and the user has been saved.
    """
    user = get_object_or_404(User, pk=id)
    initial = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': user.get_profile().phone,
        'role': user.get_profile().role,
        'language': user.get_profile().language
    }

    if request.method == 'POST':
        form = forms.UserProfileForm(
            request.POST, initial=initial, user=user, admin=request.user)

        if form.is_valid():
            profile = user.get_profile()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            profile.phone = form.cleaned_data['phone']
            profile.role = form.cleaned_data['role']
            #profile.language = form.cleaned_data['language']
            profile.save()

            user.email = form.cleaned_data['email']
            user.save()

            if profile.role == models.UserProfile.ROLE_ADMIN:
                group_profile, created = models.UserGroupProfile.objects.get_or_create(
                    user=user, group=form.cleaned_data['group'])

            if form.cleaned_data['send_email']:
                send_email(recipient=user, user=request.user,
                        msg_ident=MailTemplate.MSG_IDENT_DATA_EDIT)

            return bls_django.HttpResponseCreated()
    else:
        form = forms.UserProfileForm(initial=initial, admin=request.user)

    return render(request, 'management/dialogs/edit_user.html', {
        'form': form,
        'edited_user': user,
    })

@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def reset_password(request, id):
    user = get_object_or_404(User, pk=id)
    new_password = User.objects.make_random_password()
    send_email(recipient=user, user=request.user,
            msg_ident=MailTemplate.MSG_IDENT_PASSWORD,
            msg_data={"[password]":new_password})
    user.set_password(raw_password=new_password)
    user.save()
    return bls_django.HttpJsonResponse({'status': 'OK'})

@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def toggle_group_manager(request, user_id, group_id):
    user = get_object_or_404(User, pk=user_id)
    group = get_object_or_404(Group, pk=group_id)
    try:
        group_profile = models.UserGroupProfile.objects.get(user=user,
                                                            group=group)
        if group_profile.access_level==models.UserGroupProfile.LEVEL_FULL_ADMIN:
            group_profile.access_level=models.UserGroupProfile.LEVEL_HALF_ADMIN
        else:
            group_profile.access_level=models.UserGroupProfile.LEVEL_FULL_ADMIN
            template = MailTemplate.for_user(request.user, type=MailTemplate.TYPE_INTERNAL,
                                             identifier=MailTemplate.MSG_IDENT_RECEIVE_RIGHT)[0]
            params_dict={'[groupname]':group.name}
            if (template.send_msg != 'F'):
                send_message(sender=request.user,
                            recipients_ids=[user.id],
                            subject=template.populate_params_to_text(template.subject, params_dict),
                            body=template.populate_params(params_dict))
    except models.UserGroupProfile.DoesNotExist, e:
        group_profile = models.UserGroupProfile(user=user,
                                                group=group,
                                                access_level=models.UserGroupProfile.LEVEL_FULL_ADMIN)

    group_profile.save()

    return bls_django.HttpJsonResponse({'status': 'OK'})


@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def toggle_has_card(request, id):
    user = get_object_or_404(User, pk=id)
    profile = user.get_profile()
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')
    profile.has_card = data['has_card']
    profile.save()
    return bls_django.HttpJsonResponse({'status': 'OK'})

@http_decorators.require_POST
def set_users_is_active_flag(request, id, is_active):
    user = get_object_or_404(User, pk=id)
    user.is_active = is_active
    user.save()
    return bls_django.HttpJsonResponse({'status': 'OK'})

@decorators.is_superadmin
def activate_user(request, id):
    """Activates user by id

    :param request: Request.
    :param id: User id,

    Return values:
    - 200 if user is successfully activated.
    - 404 if user is not found..
    - 405 if request is not POST request.
    """
    return set_users_is_active_flag(request, id, True)

@decorators.is_admin_or_superadmin
def deactivate_user(request, id):
    """Deactivates user by id

    :param request: Request.
    :param id: User id,

    Return values:
    - 200 if user is successfully deactivated.
    - 404 if user is not found..
    - 405 if request is not POST request.
    """
    return set_users_is_active_flag(request, id, False)

def _set_courses_to_assign_state_if_no_users_use_it(courses):
    for course in courses:
        if TrackingEvent.objects.filter(segment__course=course).count() == 0 and \
           course.get_state().code() in [ActiveInUse.CODE, DeactivatedUsed.CODE]:
            course.get_state().act("remove_user")


@decorators.is_admin_or_superadmin
def delete_user(request, id):
    """Removes user by id and all associated objects.

    :param request: Request.
    :param id: User id,

    Return values:
    - 200 if user is successfully deleted.
    - 404 if user is not found..
    - 405 if request is not POST request.
    """

    if request.method == 'POST':
        send_goodbye = False
        if request.GET.get('send_goodbye_email') != 'false':
            send_goodbye = True

        if request.user.get_profile().role == models.UserProfile.ROLE_SUPERADMIN:
            user = get_object_or_404(User, pk=id)

            _delete_user_by_superadmin(user, request.user, send_goodbye)

            return bls_django.HttpJsonOkResponse()
        else:
            try:
                user = User.objects.get(id=id, userprofile__role=models.UserProfile.ROLE_USER)

                if not set(user.groups.all()).issubset(set(request.user.groups.all())):
                    return bls_django.HttpJsonResponse({'status': 'ERROR',
                                                        'messages': _('User has groups not managed by this admin.')})

                if TrackingEvent.objects.filter(participant=id).count():
                    return bls_django.HttpJsonResponse({'status': 'ERROR', 'messages': _('User has started course.')})
                else:
                    if send_goodbye:
                        send_email(recipient=user, user=request.user,
                                msg_ident=MailTemplate.MSG_IDENT_GOODBYE)
                    Report.objects.filter(user=user).update(is_deleted=True, user=None)
                    groups = user.groups.all()
                    user.delete()
                    for g in groups:
                        g.groupprofile.save()

                    return bls_django.HttpJsonOkResponse()
            except User.DoesNotExist:
                return bls_django.HttpJsonResponse({'status': 'ERROR',
                                                'messages': _('User with ID %s is not eligable for deletion') % id})
    else:
        return render(request
                    ,'management/dialogs/remove_user.html',
                    {'user_id': id})


def _delete_user_by_superadmin(user_to_delete, user_who_removes, send_goodbye):
    if send_goodbye:
        send_email(recipient=user_to_delete, user=user_who_removes,
                   msg_ident=MailTemplate.MSG_IDENT_GOODBYE)

    Course.objects.filter(groups__user=user_to_delete).update(owner=user_who_removes)
    File.objects.filter(owner=user_to_delete).update(owner=user_who_removes)
    CourseGroup.objects.filter(assigner=user_to_delete).update(assigner=user_who_removes)
    Collection.objects.filter(owner=user_to_delete).delete()
    Message.objects.filter(Q(sender=user_to_delete) | Q(recipient=user_to_delete)).delete()
    Report.objects.filter(user=user_to_delete).update(is_deleted=True, user=None)
    Report.objects.filter(admin=user_to_delete).update(is_deleted=True, admin=None)

    courses = list(Course.objects.filter(groups__user=user_to_delete))
    user_to_delete.delete()
    _set_courses_to_assign_state_if_no_users_use_it(courses)

@decorators.is_superadmin
def delete_users_from_csv(request):

    if request.method == 'POST':
        form = forms.DeleteUsersFromCsvForm(request.POST, request.FILES)

        if form.is_valid():
            send_goodbye = form.cleaned_data['send_goodbye_email']
            file = form.cleaned_data['file']
            row_num = sum(1 for line in file)
            status_msg = {'infos': [], 'errors': []}

            if row_num > settings.MANAGEMENT_CSV_LINES_MAX:
                status_msg['errors'].append(_('Imported file has more than maximal number of lines (%d)')
                                            % (settings.MANAGEMENT_CSV_LINES_MAX,))
            else:
                users_data = StringIO.StringIO()
                for chunk in file.chunks():
                    if chunk.startswith(codecs.BOM_UTF8):
                        users_data.write(chunk.lstrip(codecs.BOM_UTF8))
                    else:
                        users_data.write(chunk)
                users_data.seek(0)

                rows = models.UnicodeReader(users_data)
                for row in rows:
                    if len(row) > 0:
                        username = row[0]

                        if request.user.username != username:
                            try:
                                user = User.objects.get(username=username)
                                _delete_user_by_superadmin(user, request.user, send_goodbye)
                                status_msg['infos'].append(_("User successfully deleted %s") % username)
                            except User.DoesNotExist:
                                status_msg['errors'].append(_("User %s not found") % username)
                        else:
                            status_msg['infos'].append(_("Unable to delete %s. You can't remove yourself.")%username)
                status_msg["row_num"] = row_num

            return render(request,
                                      'management/import_csv.html', {'result': status_msg,
                                                                     'title': _("Results of removed users"),
                                                                     'action': 'delete'})
    return render(request,
                                  'management/import_csv.html',
                                  {'form': forms.DeleteUsersFromCsvForm(), 'title': _("Remove users listed in the selected file"),
                                   'subtitle': _("remove users")})

@decorators.is_admin_or_superadmin
def list_users(request):
    """Returns all users and groups in the JSON format.

    :param request: Request.

    Return values:
    - 200 and JSON encoded list of users and groups.
    """

    data = {
        'users': {},
        'groups': {},
        'mygroups': {},
        'memberships': {},
        'ssuper': request.user.get_profile().role == models.UserProfile.ROLE_SUPERADMIN,
        'my_id': request.user.id,
        }

    mygroups = request.user.groups.filter(id__in=models.UserGroupProfile
                                                     .objects.filter(user=request.user,
                                                     access_level=models.UserGroupProfile.LEVEL_FULL_ADMIN)
                                                     .values_list('group__id'))
    for mygroup in mygroups:
        data['mygroups'][mygroup.id] = {
            'id': mygroup.id,
            'name': mygroup.name,
            }

    for group in Group.objects.all():
        self_register_enabled = False
        try:
            self_register_enabled = group.groupprofile.self_register_enabled
        except models.GroupProfile.DoesNotExist:
            pass
        data['groups'][group.id] = {
            'id': group.id,
            'name': group.name,
            'self_register_enabled': self_register_enabled,
            }
    if request.user.get_profile().role == models.UserProfile.ROLE_SUPERADMIN:
        users = User.objects.all()
    else:
        users = User.objects.exclude(id=request.user.id)

    for user in users:
        data['users'][user.id] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'has_tracking': bool(TrackingEvent.objects.filter(participant=user.id).count()),
            'phone': user.get_profile().phone,
            'role': user.get_profile().role,
            'is_active': user.is_active,
            'activation_allowed': request.user.get_profile().role == models.UserProfile.ROLE_SUPERADMIN,
            'user_type': user.get_profile().get_user_type(),
            'user_type_translated': _(user.get_profile().get_user_type()),
            'ldap_user': user.get_profile().get_ldap_marker(),
            'plus_user': user.get_profile().get_sales_plus_marker(),
            'manages': []
            }
        for group_attrs in models.UserGroupProfile.objects\
                            .filter(user=user,
                                    access_level=models.UserGroupProfile.LEVEL_FULL_ADMIN)\
                            .values('group__id').order_by('group__name'):
            data['users'][user.id]['manages'].append(group_attrs['group__id'])
        for group in user.groups.all():
            data['memberships'].setdefault(str(group.id), []).append(user.id)


    if request.user.get_profile().role == models.UserProfile.ROLE_SUPERADMIN:
        groupless_users = User.objects.annotate(groups_count=db_models.aggregates.Count('groups'))\
                                        .filter(groups_count=0).values('id')
    else:
        groupless_users = User.objects.exclude(
            userprofile__role=models.UserProfile.ROLE_SUPERADMIN).exclude(
                id=request.user.id).annotate(groups_count=db_models.aggregates.Count('groups'))\
                                    .filter(groups_count=0).values('id')

    data['groupless'] = [user['id'] for user in groupless_users]

    return bls_django.HttpJsonResponse(data)



@transaction.commit_manually
@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def memberships(request, group_id):
    """Manages users' membership in groups.

    This view should be used as a webservice for Ajax requests.

    For details about the request and response formats check section
    `Group membership management` in ``docs/ws-spec.rst``.

    :param request: Request.
    :param group_id: Id of the group to operate on.

    Return values:
    - 200 if message has been processed. Check the status field in the reponse
      message to verify if action has been successful.
    - 400 if we cannot parse the request or invalid
      action has been specified in the request.
    - 404 if the specified group doens't exist.
    - 405 if request is not POST
    """

    group = get_object_or_404(Group, pk=group_id)

    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    action = data.get('action')
    if action == 'add':
        for id in data.get('members', []):
            try:
                user = User.objects.get(pk=id)
                user.groups.add(group)
                group.groupprofile.save()
            except User.DoesNotExist:
                transaction.rollback()
                response = {
                    'status': 'ERROR',
                    'messages': [_('User with ID %d does not exist.') % (id,)],
                    }
                return bls_django.HttpJsonResponse(response)
        template = MailTemplate.for_user(request.user, type=MailTemplate.TYPE_INTERNAL,
                                            identifier=MailTemplate.MSG_IDENT_WELCOME_GROUP)[0]

    elif action == 'remove':
        for id in data.get('members', []):
            try:
                user = User.objects.get(pk=id)
                user.groups.remove(group)
                group.groupprofile.save()
            except User.DoesNotExist:
                transaction.rollback()
                response = {
                    'status': 'ERROR',
                    'messages': [_('User with ID %d does not exist.') % (id,)],
                    }
                return bls_django.HttpJsonResponse(response)
        template = MailTemplate.for_user(request.user, type=MailTemplate.TYPE_INTERNAL,
                                         identifier=MailTemplate.MSG_IDENT_GOODBYE)[0]
    else:
        return http.HttpResponseBadRequest(_('Invalid action specified.'))

    params_dict={'[groupname]':group.name}
    if (template.send_msg != 'F'):
        send_message(sender=request.user,
                    recipients_ids=data['members'],
                    subject=template.populate_params_to_text(template.subject, params_dict),
                    body=template.populate_params(params_dict))

    transaction.commit()

    response = {'status': 'OK'}
    return bls_django.HttpJsonResponse(response)


@decorators.is_admin_or_superadmin
def create_group(request):
    """Handles group creation.

    :param request: Request.

    Return values:
	- 200 if user is requesting the form (GET request), or if there are
	  validation errors (POST request).
	- 201 if everything is OK and the group has been saved.
    """

    if request.method == 'POST':
        form = forms.GroupEditForm(request.POST)
        if form.is_valid():
            group = Group(name=form.cleaned_data['name'])
            group.save()
            (gp, created) = models.GroupProfile.objects.get_or_create(group=group)
            gp.save()

            request.user.groups.add(group)
            group.groupprofile.save()
            request.user.save()

            groupProfile = models.UserGroupProfile(user=request.user,
                            group=group,
                            access_level=models.UserGroupProfile.LEVEL_FULL_ADMIN)
            groupProfile.save()


            return http.HttpResponse('{"id": "' + str(group.id) + '"}', None, 201)
    else:
        form = forms.GroupEditForm()

    return render(request, 'management/edit_group.html', {
        'form': form,
        })


@decorators.is_admin_or_superadmin
def edit_group(request, id):
    """Handles group modification.

    :param request: Request.
    :param id: Id of the group.

    Return values:
    - 200 if user is requesting the form (GET request), or if there are
      validation errors (POST request).
    - 201 if everything is OK and the group has been updated.
    """

    group = get_object_or_404(Group, pk=id)
    initial = {'name': group.name}

    if request.method == 'POST':
        form = forms.GroupEditForm(request.POST, initial=initial, group=group)
        if form.is_valid():
            group.name = form.cleaned_data['name']
            group.save()
            return http.HttpResponse('{"id": "' + str(group.id) + '"}', None, 201)
    else:
        form = forms.GroupEditForm(initial=initial)

    return render(request, 'management/edit_group.html', {
        'form': form,
        'group': group,
        })

@decorators.is_superadmin
@http_decorators.require_POST
def groups_self_register(request):
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    action = data.get('action')
    if action == 'enable':
        for id in data.get('groups', []):
            try:
                group = Group.objects.get(pk=id)
            except Group.DoesNotExist:
                response = {
                    'status': 'ERROR',
                    'messages': [_('Group with ID %d does not exist.') % (id,)],
                    }
                return bls_django.HttpJsonResponse(response)

            try:
                group_profile = group.groupprofile
            except models.GroupProfile.DoesNotExist:
                group_profile = models.GroupProfile(group=group)
            group_profile.self_register_enabled = True
            group_profile.save()
    elif action == 'disable':
        for id in data.get('groups', []):
            try:    
                group = Group.objects.get(pk=id)
            except Group.DoesNotExist:
                response = {
                    'status': 'ERROR',
                    'messages': [_('Group with ID %d does not exist.') % (id,)],
                    }
                return bls_django.HttpJsonResponse(response)
            
            try:
                group_profile = group.groupprofile
            except models.GroupProfile.DoesNotExist:
                group_profile = models.GroupProfile(group=group)
            group_profile.self_register_enabled = False
            group_profile.save()
    else:
        return http.HttpResponseBadRequest(_('Invalid action specified.'))

    response = {'status': 'OK'}
    return bls_django.HttpJsonResponse(response)


@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def group_users(request, id):
    """
        gets users assigned to given group
    """
    users_dict = {}
    for user in User.objects.filter(groups__id=id,
        userprofile__role__in=[r[0] for r in models.UserProfile.ROLES_CUTED]):

        users_dict[user.id] = models.serialize_user(user)
    
    # assign to all
    print id
    if id=='-2':
        return bls_django.HttpJsonResponse(
                    {0: {'role': 0,
                         'id': 0, 
                         'name': u'Everyone'}
                    })
        
    return bls_django.HttpJsonResponse(users_dict)

@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def user_groups(request, id):
    groups_dict = {}
    for group in get_object_or_404(User, id=id).groups.all():
        groups_dict[group.id] = models.serialize_group(group)
    return bls_django.HttpJsonResponse(groups_dict)

@decorators.is_admin_or_superadmin
def groups_list(request):
    """Handles groups list request. For admin always returns his groups.
    Superadmin can parametrize request with 'my' param.

    :param request: Request.

    Return values:
    - 200 when user is requesting groups list.
    """
    show_my_groups = request.GET.get('my', '0')

    if show_my_groups == '1':
        groups = request.user.groups.all()
    else:
        groups = Group.objects.all()
    groups = groups.order_by('name')

    groups_dict = {}
    for group in groups:
        groups_dict[group.id] = models.serialize_group(group)

    return bls_django.HttpJsonResponse(groups_dict)

@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def delete_group(request, id):
    """Removes group by id and all associated objects.

    :param request: Request.
    :param id: Group id,

    Return values:
    - 200 if group is successfully removed.
    - 404 if group is not found.
    - 405 if request is not POST request.
    """
    #if (request.user.get_profile().role == models.UserProfile.ROLE_ADMIN) & \
    #                                      User.objects.exclude(id=request.user.id).filter(groups=id).count() > 0:
    #    return bls_django.HttpJsonResponse({'status': 'ERROR', "messages": "Group contains users"})

    group = get_object_or_404(Group, pk=id)
    Report.objects.filter(group=group).update(is_deleted=True, group=None)
    group.delete()
    return bls_django.HttpJsonOkResponse()

@decorators.is_admin_or_superadmin
def export_users(request, group_id):
    """
        Handles exporting users to documents of format specified by request param 'format'

         :param request: Request.
         :param group_id: Id of the group to be exported.

         Return values:

    """
    format = request.GET.get('format', 'csv')

    group = get_object_or_404(Group, pk=group_id)

    try :
        exporter = models.UserExporter(group_name=group.name, format=format)
    except models.UnknownFormatError, e:
        return http.HttpResponseBadRequest(e.reason)

    return exporter.export_users(group.user_set.all())



@decorators.is_admin_or_superadmin
@transaction.commit_manually
def import_users(request, group_id):

    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':

        form = forms.CsvImportForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']

            users_data = StringIO.StringIO()
            for chunk in file.chunks():
                users_data.write(chunk)

            users_data.seek(0)

            importer = models.UserImporter(group=group, format=file.name.lower().rpartition('.')[2], importer=request.user)

            result = {
                'result': importer.import_users(users_data, request.user,
                                          form.cleaned_data['send_email']
                        ),
                'title': _("Results of users import to group:") + group.name
            }
            return render(request, 'management/import_csv.html', result)
    else:
        form = forms.CsvImportForm()

    ctx = {
        'form': form,
        'title': _("Import users to group: ") + group.name,
        "subtitle": _("import users to group"),
        "group_id": group.id
        }
    return render(request, 'management/import_csv.html', ctx)

def admin_modules(request):
    report = reports.get_report_from_request(request)

    if report.group_id:
        groups = Group.objects.filter(id=report.group_id)
    else:
        groups = reports.get_owner_groups(report.owner_id, report.show_all)

    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    modules = Course.objects.filter(groups__in=groups,
                                    state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()

    admin_modules = {}
    for module in modules:
        admin_modules[module.owner] = 0

    for module in modules:
        admin_modules[module.owner] += 1

    for user in admin_modules:
        writer.writerow([user.first_name + ' ' + user.last_name, str(admin_modules[user])])

    return reports.get_csv('admin_modules.csv', result)

@http_decorators.require_GET
@login_required
def user_profile(request):
    return render(request, 'management/user_profile.html')

@login_required
def user_password_change(request):
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            if request.user.id != form.cleaned_data['user_id']:
                return http.HttpResponseBadRequest('Invalid user id.')
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()

            send_email(recipient=request.user, user=request.user,
                    msg_ident=MailTemplate.MSG_IDENT_PASSWORD,
                    msg_data={"[username]":request.user.username,
                        "[password]":form.cleaned_data['new_password']})

            return http.HttpResponse(status=200)
    else:
        form = forms.ChangePasswordForm(initial={'user_id': request.user.id})
    return render(request,
                              'management/user_pass_change.html',
                              {'form': form})

def login_screen(request):
    request.session['languages'] = settings.AVAILABLE_LANGUAGES
    if request.method == 'POST':
        language = request.POST['language']
        request.session['django_language'] = language
        translation.activate(language)
        return login(request, authentication_form=AuthenticationForm)
    else:
        default_lang = 'en'
        request.session['django_language'] = default_lang or settings.LANGUAGE_CODE
        translation.activate(request.session['django_language'])

        gui_logo_filename = ''#admin_models.get_entry_val(ConfigEntry.GUI_LOGO_FILE) or ''
        gui_logo_filename_parts = os.path.splitext(gui_logo_filename)
        gui_logo_file_ext = gui_logo_filename_parts[1] or ''
        logo_file_url = ''
        if gui_logo_filename:
            logo_file_url = settings.CSS_TEMPLATES_URL +'/'+ settings.CUSTOM_LOGO_FILE_NAME + gui_logo_file_ext
        return render(request, 'registration/login.html',
        {
            "REGISTRATION_OPEN": settings.REGISTRATION_OPEN,
            "logo_file_url": logo_file_url,
        })


@http_decorators.require_GET
def one_click_link_smm(request):
    token = request.GET.get('token')

    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        
        if one_click_link_token.expired:
            return render(request,
                    'registration/login.html', {"ocl_expired": True})

        from django.contrib.auth import login as auth_login
        one_click_link_token.user.backend = "django.contrib.auth.backends.ModelBackend"

        if not one_click_link_token.user.is_active:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        auth_login(request, one_click_link_token.user)

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect_to_login("/")

@http_decorators.require_GET
def one_click_link(request):
    token = request.GET.get('token')

    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        
        if one_click_link_token.expired:
            return render(request,
                    'registration/login.html', {"ocl_expired": True})

        from django.contrib.auth import login as auth_login
        one_click_link_token.user.backend = "django.contrib.auth.backends.ModelBackend"

        if not one_click_link_token.user.is_active:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        auth_login(request, one_click_link_token.user)

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect_to_login("/")

@csrf_exempt
@http_decorators.require_POST
def web_service_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = None
    if username and password:
        user = authenticate(username=username, password=password)

    if not user:
        return HttpJsonResponse({'status': 'ERROR', 'message': 'Invalid credentials'})
    elif not user.is_active:
        return HttpJsonResponse({'status': 'ERROR', 'message': 'User is not active'})
    else:
        from django.contrib.auth import login as auth_login
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth_login(request, user)
        return HttpJsonResponse({'status': 'OK'})


@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def ocl_expire(request, id):
    try:
        ocl = OneClickLinkToken.objects.get(pk=id)
    except OneClickLinkToken.DoesNotExist:
        return HttpJsonResponse({'status': 'ERROR',
            'message': unicode(_('Token does not exist'))})
    
    form = forms.OCLExpirationForm(request.POST)
    if form.is_valid():
        from datetime import date
        if form.cleaned_data['expires_on']:
            ocl.expires_on = form.cleaned_data['expires_on']
            if form.cleaned_data['expires_on'] < date.today():
                ocl.expired = True
        else:
            ocl.expires_on = date.today()
            ocl.expired = True
    else:
        return HttpJsonResponse({'status': 'ERROR',
            'message': unicode(_('Date is invalid'))})

    ocl.save()
    return HttpJsonResponse({'status': 'OK', "expired": ocl.expired})

# vim: set et sw=4 ts=4 sts=4 tw=78:
