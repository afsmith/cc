# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#
#

"""Django views.
"""

from datetime import datetime
import json, StringIO, logging, urllib

from django.conf import settings
from django import http
from django.contrib.auth import models as auth_models
from django.contrib.auth import decorators as auth_decorators
from django.db import models as db_models, transaction
from django.db.models import Sum, Max
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.views.decorators import http as http_decorators
from django.shortcuts import render

from bls_common import bls_django
from content import models as cont_models, serializers
import content
from content.course_states import Active, ActiveAssign, ActiveInUse, Removed
from content.models import DownloadEvent
from management import models as manage_models
from management.models import OneClickLinkToken, UserProfile
from management.views import one_click_link
#from messages_custom.models import MailTemplate
#from messages_custom.utils import send_email, send_message
from plato_common import decorators
from tracking.models import ScormActivityDetails, TrackingEventService, active_modules_with_track_ratio, module_with_track_ratio
from tracking.utils import progress_formatter
#from reports import reports
#from reports.models import Report
from management.forms import OCLExpirationForm



logger = logging.getLogger("assignments")

"""
is_admin_or_superadmin = decorators.user_passes_test(
    lambda u: u.get_profile().role in (
        manage_models.UserProfile.ROLE_ADMIN,
        manage_models.UserProfile.ROLE_SUPERADMIN)
    )

is_user = decorators.user_passes_test(
    lambda u: u.get_profile().role == manage_models.UserProfile.ROLE_USER
    )
"""

def _assign_to_all_groups(assignments, group_id, req_user, is_sendmail, allow_login, saved_template, saved_content, saved_subject, add_one_click_link, ocl_expires_on, host=''):
    curr_time = datetime.now()
    groups = auth_models.Group.objects.all()
    m_assigned_to_all = []
    for c in cont_models.Course.objects.all():
        if c.is_assigned_to_all():
            m_assigned_to_all.append(c)
    for group in groups:
        for module in group.course_set.all():
            if (str(module.id) not in assignments[group_id]) and (module in m_assigned_to_all):
                cont_models.CourseGroup.objects.filter(course=module, group=group).delete()

                if module.get_state().has_code(ActiveAssign.CODE) and cont_models.CourseGroup.objects.filter(course=module).count() == 0:
                    module.get_state().act('remove_assignments')

        assigned_modules = []
        for module_id in assignments[group_id]:
            try:
                module = cont_models.Course.objects.get(pk=module_id)
            except cont_models.Course.DoesNotExist:
                transaction.rollback()
                response = {
                    'status': 'ERROR',
                    'messages': ['Course with ID %s does not exist.' % module_id],
                    }
                return bls_django.HttpJsonResponse(response)
            if module not in group.course_set.all():
                course_group = cont_models.CourseGroup(group=group, course=module, assigned_on=curr_time, assigner=req_user)
                course_group.save()
                assigned_modules.append(module)

                if module.get_state().has_code(Active.CODE):
                    module.get_state().act('assign')

        if is_sendmail:
            for user in group.user_set.filter(userprofile__role__gte=manage_models.UserProfile.ROLE_USER,
                                            is_active=True):
                modules_list_tmp = ''
                ocl = None
                if not user.get_profile().ldap_user and add_one_click_link:
                    #create new ocl per assigment
                    
                    ocl = OneClickLinkToken.objects.create(user=user, expires_on=ocl_expires_on,
                                                            allow_login=allow_login)
                    for i in range(len(assigned_modules)):
                        ocl_link = MailTemplate.ONE_CLICK_LINK_SMM % (host, int(assigned_modules[i].id), ocl.token)
                        if not settings.SALES_PLUS:
                            ocl_link = MailTemplate.ONE_CLICK_LINK % (host, ocl.token)
                        
                        if len(assigned_modules)==1:
                            modules_list_tmp += assigned_modules[i].title
                        else:
                            modules_list_tmp += ''.join((str(i+1),'."',str(assigned_modules[i].title),
                                                        '"<br />\n', str(ocl_link), '<br />\n'))
                        
                    prevent_user_plus=False                       
                else:
                    for i in range(len(assigned_modules)):
                        if len(assigned_modules)==1:
                            modules_list_tmp += assigned_modules[i].title
                        else:
                            modules_list_tmp += ''.join((str(i+1),'."',str(assigned_modules[i].title),'"<br />\n'))
                    prevent_user_plus=True
                    
                is_ocl = (add_one_click_link and True) or False
                if modules_list_tmp:
                    msg_ident = MailTemplate.MSG_IDENT_ADD_ASSIGNMENT
                    msg_data={'[groupname]': group.name,
                            '[moduletitle]': modules_list_tmp}
                    if len(assigned_modules) > 1:
                        msg_data={'[groupname]': group.name,
                                '[moduleslist]': modules_list_tmp}
                        msg_ident = MailTemplate.MSG_IDENT_ADD_MULTI_ASSIGNMENTS
                    if add_one_click_link:
                        msg_data['[oneclicklink]'] = ocl_link
                        msg_ident = MailTemplate.MSG_IDENT_ADD_ASSIGNMENT_OCL

                    send_email(recipient=user, user=req_user,
                            msg_ident=msg_ident,
                            msg_data=msg_data,
                            prevent_user_plus=prevent_user_plus,
                            template_content=saved_content or None,
                            template_subject=saved_subject or None,
                            courses=assigned_modules or None,
                            ocl=ocl)

@transaction.commit_manually
@decorators.is_admin_or_superadmin
def group_modules(request):

    """
        Handles groups-modules assignments.

        :param request: Request

        return values:
        - 200
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.raw_post_data)
            assignments = data['assignments']
            add_one_click_link = data['add_one_click_link'] if 'add_one_click_link' in data else False
            ocl_expires_on = None
            form = OCLExpirationForm(data)
            if form.is_valid():
                ocl_expires_on = form.cleaned_data['expires_on']

            is_sendmail = data['is_sendmail'] if 'is_sendmail' in data else False
            allow_login = data.get('allow_login', False)
            # personalized template {{{
            saved_template = data.get('savedTemplate', {})
            saved_content = ''
            saved_subject = ''
            if saved_template:
                saved_content = saved_template.get('content', '')
                saved_subject = saved_template.get('subject', '')
            #}}}
        except ValueError:
            response = {
                    'status': 'ERROR',
                    'messages': ['Invalid JSON content.'],
                    }
            return bls_django.HttpJsonResponse(response)

        curr_time = datetime.now()

        for group_id in assignments.keys():
            #
            # Checking if group has associations to modules which should be removed
            #
            assign_to_all = False
            try:
                if group_id == '-2':
                    _assign_to_all_groups(assignments, group_id, request.user, is_sendmail, allow_login, saved_template, saved_content, saved_subject, add_one_click_link, ocl_expires_on, host=request.get_host())
                    assign_to_all = True
                else:
                    group = auth_models.Group.objects.get(pk=group_id)
            except auth_models.Group.DoesNotExist:
                transaction.rollback()
                response = {
                    'status': 'ERROR',
                    'messages': ['Group with ID %s does not exist.' % group_id],
                    }
                return bls_django.HttpJsonResponse(response)

            if not assign_to_all:
                for module in group.course_set.all():
                    if str(module.id) not in assignments[group_id]:
                        cont_models.CourseGroup.objects.filter(course=module, group=group).delete()

                        if module.get_state().has_code(ActiveAssign.CODE) and cont_models.CourseGroup.objects.filter(course=module).count() == 0:
                            module.get_state().act('remove_assignments')

                #
                # Checking if group has any new associations to modules and saving them
                #
                assigned_modules = []
                for module_id in assignments[str(group.id)]:
                    try:
                        module = cont_models.Course.objects.get(pk=module_id)
                    except cont_models.Course.DoesNotExist:
                        transaction.rollback()
                        response = {
                            'status': 'ERROR',
                            'messages': ['Course with ID %s does not exist.' % module_id],
                            }
                        return bls_django.HttpJsonResponse(response)
                    if module not in group.course_set.all():
                        course_group = cont_models.CourseGroup(group=group, course=module, assigned_on=curr_time, assigner=request.user)
                        course_group.save()
                        assigned_modules.append(module)

                        if module.get_state().has_code(Active.CODE):
                            module.get_state().act('assign')

                if is_sendmail:
                    for user in group.user_set.filter(userprofile__role__gte=manage_models.UserProfile.ROLE_USER,
                                                    is_active=True):
                        modules_list_tmp = ''
                        ocl = None
                        if not user.get_profile().ldap_user and add_one_click_link:
                            #create new ocl per assigment
                            
                            ocl = OneClickLinkToken.objects.create(user=user, expires_on=ocl_expires_on,
                                                                    allow_login=allow_login)
                            for i in range(len(assigned_modules)):
                                ocl_link = MailTemplate.ONE_CLICK_LINK_SMM % (request.get_host(), int(assigned_modules[i].id), ocl.token)
                                if not settings.SALES_PLUS:
                                    ocl_link = MailTemplate.ONE_CLICK_LINK % (request.get_host(), ocl.token)
                                
                                if len(assigned_modules)==1:
                                    modules_list_tmp += assigned_modules[i].title
                                else:
                                    modules_list_tmp += ''.join((str(i+1),'."',str(assigned_modules[i].title),
                                                                '"<br />\n', str(ocl_link), '<br />\n'))
                                
                            prevent_user_plus=False                       
                        else:
                            for i in range(len(assigned_modules)):
                                if len(assigned_modules)==1:
                                    modules_list_tmp += assigned_modules[i].title
                                else:
                                    modules_list_tmp += ''.join((str(i+1),'."',str(assigned_modules[i].title),'"<br />\n'))
                            prevent_user_plus=True
                            
                        is_ocl = (add_one_click_link and True) or False
                        if modules_list_tmp:
                            msg_ident = MailTemplate.MSG_IDENT_ADD_ASSIGNMENT
                            msg_data={'[groupname]': group.name,
                                    '[moduletitle]': modules_list_tmp}
                            if len(assigned_modules) > 1:
                                msg_data={'[groupname]': group.name,
                                        '[moduleslist]': modules_list_tmp}
                                msg_ident = MailTemplate.MSG_IDENT_ADD_MULTI_ASSIGNMENTS
                            if add_one_click_link:
                                msg_data['[oneclicklink]'] = ocl_link
                                msg_ident = MailTemplate.MSG_IDENT_ADD_ASSIGNMENT_OCL

                            send_email(recipient=user, user=request.user,
                                    msg_ident=msg_ident,
                                    msg_data=msg_data,
                                    prevent_user_plus=prevent_user_plus,
                                    template_content=saved_content or None,
                                    template_subject=saved_subject or None,
                                    courses=assigned_modules or None,
                                    ocl=ocl)
                                     
        transaction.commit()
        return bls_django.HttpJsonResponse({'status':'OK', 'messages': []})

    else:
        serialized_set = {}
        groups = auth_models.Group.objects.all()
        courses = cont_models.Course.objects.filter(Q(state_code=ActiveAssign.CODE) |
                                                  Q(state_code=ActiveInUse.CODE) |
                                                  Q(state_code=Active.CODE))
        serialized_assign_to_all = {}
        groups_count = groups.count()
        for group in groups:
            serialized_set[group.id] = {}
            for module in group.course_set.filter(Q(state_code=ActiveAssign.CODE) |
                                                  Q(state_code=ActiveInUse.CODE) |
                                                  Q(state_code=Active.CODE)):
                module_dict = serializers.serialize_course(module, request.user, TrackingEventService())['meta']
                module_dict['short_title'] = module_dict['title'][:7] + '...'
                module_dict['owner'] = ' '.join((module.owner.first_name,module.owner.last_name))
                serialized_set[group.id][module.id] = module_dict
                module_group = cont_models.CourseGroup.objects.filter(course=module)\
                                                              .order_by('group')\
                                                              .distinct('group')
                if module_group.count()==groups_count:
                    serialized_assign_to_all[module.id] = module_dict
        serialized_set[-2] = serialized_assign_to_all


        return bls_django.HttpJsonResponse(serialized_set)

@decorators.is_user
def user_modules(request):

    """
        Handles requests for modules assigned to groups of logged in user.

         return values:
         - 200 if request successfully fulfilled, response contains JSON object containing list of
                modules assigned to groups of specified user,
         - 302 if logged in user is not a normal user
    """
    modules = []
    finished_modules = []
    cg = {}

    for course_group in cont_models.CourseGroup.objects.filter(
        Q(group__in=request.user.groups.all()) &
        (Q(course__state_code=ActiveAssign.CODE) | Q(course__state_code=ActiveInUse.CODE))):
        value = None;
        try:
            value = cg[course_group.course]
            if value.assigned_on > course_group.assigned_on:
                cg[course_group.course] = course_group
        except KeyError, e:
            cg[course_group.course] = course_group

    result = sorted(cg.values(), key=lambda value: value.assigned_on, reverse=True)
    for course_group in result:
        course_group.course.segments_with_learnt_flag = TrackingEventService().segments(request.user.id, course_group.course.id)
        # -- a course is considered new only if it does not have any tracking history connected to working user
        course_group.course.is_new = 0
        for segment in course_group.course.segments_with_learnt_flag:
            course_group.course.is_new += len(TrackingEventService().trackingHistory(segment.id, request.user.id))
            segment.available=True
        course_group.course.is_new = not bool(course_group.course.is_new)
        course_group.course.duration = cont_models.Segment.objects.filter(course=course_group.course, track=0).aggregate(Sum('file__duration'))['file__duration__sum']
        if module_with_track_ratio(request.user.id, course_group.course.id) == 1:
            course_group.course.is_new = False
            finished_modules.append(course_group.course)
        else:
            if not course_group.course.allow_skipping:
                course_group.course.segments_with_learnt_flag = cont_models.\
                                                        get_segments_with_available_flag(course_group.course.segments_with_learnt_flag)
            modules.append(course_group.course)


    ctx = {
       'courses': modules,
       'finished_courses': finished_modules
    }

    return render(request, "assignments/user_modules.html", ctx)


@auth_decorators.login_required
def dashboard(request):
    """
        Handles initial screen display. Called when empty context is requested.
    """
    if request.user.get_profile().role in (
        manage_models.UserProfile.ROLE_ADMIN,
        manage_models.UserProfile.ROLE_SUPERADMIN
    ):
        return admin_status(request)
    else:
        return user_modules(request)


@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def admin_status(request):
    """
        Handles preparing the screen for admin-status page.
        200 - if request successfully fulfilled, returned context contains:
                'groups' - list of groups (all groups for superadmin),
                'data' - data of every group (id, courses, users_data)
        405 - if request method is not GET.
    """

    groups = []

    if request.user.get_profile().role == manage_models.UserProfile.ROLE_ADMIN:
        my_groups = request.user.groups.all().order_by("name")
        groups = request.user.groups.all().order_by("name")

    elif request.user.get_profile().role == manage_models.UserProfile.ROLE_SUPERADMIN:
        my_groups = request.user.groups.all().order_by("name")
        groups = auth_models.Group.objects.all().order_by("name")

    recent_content = cont_models.File.objects.filter(status__in=(cont_models.File.STATUS_AVAILABLE,
                                cont_models.File.STATUS_EXPIRED), owner=request.user)\
                                .order_by('created_on').reverse()[0:5]
                                
    recent_modules = cont_models.Course.objects.filter(owner=request.user)\
                          .filter(~db_models.query_utils.Q(state_code=Removed.CODE))\
                          .order_by('created_on').reverse()[0:5]
                          
    recent_reports = Report.objects.filter(owner=request.user,is_template=False)\
                          .order_by('created_on').reverse()[0:5]

    group_data = {}
    
    def build_group_data(group):
        group_data[group] = {}
        group_data[group]['user_count'] = 0
        group_data[group]['admin_count'] = 0
        group_data[group]['module_ratio'] = dict()
        group_data[group]['id'] = group.id
        #group_data[group]['courses']= group.course_set.annotate(
        #    segments_count=db_models.aggregates.Count("segment")).filter(
        #        (Q(state_code=ActiveAssign.CODE) |
        #         Q(state_code=ActiveInUse.CODE)) &
        #        ~db_models.query_utils.Q(segments_count = 0)).order_by('title')
        group_data[group]['users_data'] = []
#        def map_users(user):
#            if user.get_profile().role > manage_models.UserProfile.ROLE_ADMIN:
#                #group_data[group]['user_count'] += 1
#                mods = active_modules_with_track_ratio(user.id, group.id)
#                if len(mods) > 0:
#                    mods.reverse()
#                    
#                for row in mods:
#                    try:
#                        group_data[group]['module_ratio'][row['id']].append(float(row['ratio']))
#                    except KeyError:
#                        group_data[group]['module_ratio'][row['id']] = [float(row['ratio'])]
#         
#                group_data[group]['users_data'].append([user, mods])
#            else:
#            #    pass
#                group_data[group]['admin_count'] += 1
#        #map(map_users, group.user_set.all())
        group_data[group]['user_count'] = group.groupprofile.user_count
        
        group_data[group]['users_data'].sort(lambda x,y : cmp(x[0].last_name.lower(), y[0].last_name.lower()))
        
        #for module, ratios in group_data[group]['module_ratio'].items():
        #    group_data[group]['module_ratio'][module] = progress_formatter(sum(ratios) / len(ratios))

    map(build_group_data, groups)
        
    ctx = {
        'data': group_data,
        'groups': groups,
        'my_groups': my_groups,
        'settings': {'SALES_PLUS': settings.SALES_PLUS},
        'my_stats': [recent_content, recent_modules, recent_reports],
        'widgets': ['my_content_stats', 'my_reports_stats', 'my_modules_stats']
    }

    return render(request, 'assignments/admin_status.html', ctx)

@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def group_status(request, group_id):
    group = get_object_or_404(auth_models.Group, pk=group_id)
    group_data = {}
    group_data[group] = {}
    group_data[group]['users_data'] = []
    group_data[group]['courses']= group.course_set.annotate(
        segments_count=db_models.aggregates.Count("segment")).filter(
            (Q(state_code=ActiveAssign.CODE) |
                Q(state_code=ActiveInUse.CODE)) &
            ~db_models.query_utils.Q(segments_count = 0)).order_by('title')

    group_data[group]['module_ratio'] = {}
    for user in group.user_set.all():
        if user.get_profile().role > manage_models.UserProfile.ROLE_ADMIN:
            mods = active_modules_with_track_ratio(user.id, group.id)
            if len(mods) > 0:
                mods.reverse()
                
            for row in mods:
                try:
                    group_data[group]['module_ratio'][row['id']].append(float(row['ratio']))
                except KeyError:
                    group_data[group]['module_ratio'][row['id']] = [float(row['ratio'])]
    
            group_data[group]['users_data'].append([user, mods])

    group_data[group]['users_data'].sort(lambda x,y : cmp(x[0].last_name.lower(), y[0].last_name.lower()))

    for module, ratios in group_data[group]['module_ratio'].items():
        group_data[group]['module_ratio'][module] = progress_formatter(sum(ratios) / len(ratios))

    return render(request, 'assignments/group_details.html',
                              {'data': group_data})

@http_decorators.require_GET
def module_progress(request):
    course_id = request.GET.get('course_id', '')
    group_id = request.GET.get('group_id', '')
    course = get_object_or_404(cont_models.Course, pk=course_id)
    group = get_object_or_404(auth_models.Group, pk=group_id)
    
    users = []
    overall_ratio = 0
    for user in group.user_set.all().order_by("first_name", "last_name"):
        if all(curr_user.get('id') != user.id for curr_user in users) \
        and user.get_profile().role in [manage_models.UserProfile.ROLE_USER,
                                        manage_models.UserProfile.ROLE_USER_PLUS]:
            user_ratio = 0
            ip_count = 0
            mods = active_modules_with_track_ratio(user.id, group_id)
            if len(mods) > 0:
                mods.reverse()
            
            for row in mods:
                if row['id'] == course.id:
                    user_ratio = row['ratio']
                    ip_count = row['ip_count']
                    
            users.append({'data': user,
                          'ip_count': ip_count,
                          'ratio': progress_formatter(user_ratio)})
            overall_ratio += user_ratio
    
    if users:
        overall_ratio = progress_formatter(overall_ratio / len(users))
    
    ctx = {
        'course': course,
        'group': group,
        'module_ratio': overall_ratio,
        'settings': {'SALES_PLUS': settings.SALES_PLUS},
        'users': users,
        'status_checkbox_enabled': settings.STATUS_CHECKBOX,
    }
    return render(request, 'assignments/module_progress.html', ctx)

@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def user_progress(request):
    """
        Handles preparing the screen for user-progress page.

        :params request: Request

        200 - if request successfully fulfilled, returned context contains:
                user_obj - user whose progress is shown,
                course - course for which progress is shown,
                
        404 - if user with supplied user_id was not found or
              if course with supplied course_id was not found
        405 - if request method is not GET
    """

    user_id = request.GET.get('user_id', '')
    course_id = request.GET.get('course_id', '')

    user = get_object_or_404(auth_models.User, pk=user_id)
    course = get_object_or_404(cont_models.Course, pk=course_id)
    try:
        course_user = cont_models.CourseUser.objects.get(course=course, user=user)
    except cont_models.CourseUser.DoesNotExist:
        course_user = None

    tracking_service = TrackingEventService()
    course_ratio = module_with_track_ratio(user_id=user.id, course_id=course.id)

    segments_tracking = tracking_service.segments(user_id=user.id, course_id=course.id)
    if not course.allow_skipping:
        segments_tracking = cont_models.get_segments_with_available_flag(segments_tracking)

    segments = {}
    total_hours = 0
    total_minutes = 0
    total_seconds = 0
    for segment in segments_tracking:
        trackings = {}
        tracking_list = tracking_service.trackingHistory(segment_id=segment.id, participant_id=user.id)

        hours = 0
        minutes = 0
        seconds = 0
        for tracking in tracking_list:
            trackings[tracking['id']] = ScormActivityDetails.objects.filter(
                segment=segment,
                user=user,
                tracking__id=tracking['id']
            ) or []
            hours += int(tracking['duration'].split(":")[0])
            minutes += int(tracking['duration'].split(":")[1])
            seconds += int(tracking['duration'].split(":")[2])

        total_hours += hours
        total_minutes += minutes
        total_seconds += seconds

        segments[segment.start] = {
            'segment' : segment,
            'total_time': '%02d:%02d:%02d'%(reports.calculate_time(hours, minutes, seconds)),
            'download_count': DownloadEvent.objects.filter(segment=segment, user=user).count(),
            'trackings' : tracking_list,
            'results' : trackings
        }
    segments['total'] = '%02d:%02d:%02d' % (reports.calculate_time(
        total_hours, total_minutes, total_seconds))

    ctx = {
        'user_obj': user,
        'course': course,
        'course_user': course_user,
        'ratio': progress_formatter(course_ratio),
        'segments': segments,
        'settings': {'SALES_PLUS': settings.SALES_PLUS},
    }
    return render(request, 'assignments/user_progress.html', ctx)


def _users_per_module(owner_id, group_id=None, show_all=True):
    owner_groups = reports.get_owner_groups(owner_id, show_all)
    courses = cont_models.Course.objects.filter(groups__in=owner_groups.values_list('id', flat=True),
                                                state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()

    if group_id:
        courses = courses.filter(groups=group_id)

    course_users = {}
    for course in courses:
        course_users[course.id] = {"title" : course.title,
                                   "users_count" : str(auth_models.User.objects.filter(
                                       userprofile__role=UserProfile.ROLE_USER,
                                       groups__in=course.groups.values_list('id', flat=True),
                                       is_active=True).distinct().count())}

    return course_users

def users_per_module(request):
    report = reports.get_report_from_request(request)
    
    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)
    course_users = _users_per_module(report.owner_id, report.group_id, report.show_all)
    for id in course_users:
        writer.writerow([course_users[id]["title"], course_users[id]["users_count"]])
        
    return reports.get_csv('users_per_module.csv', result)

def published_modules(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)

    if report.group_id:
        groups = auth_models.Group.objects.filter(id=report.group_id, id__in=owner_groups)
    else:
        groups = auth_models.Group.objects.filter(id__in=owner_groups)
    
    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    for group in groups:
        modules_count = cont_models.Course.objects.filter(groups=group,
                                                          state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).count()
        writer.writerow([group.name, str(modules_count)])
    
    return reports.get_csv('published_modules.csv', result)
