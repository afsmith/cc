
import json
import logging
import StringIO

from django import http
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.conf import settings
from cc.libs.bls_common import bls_django
from cc.libs.bls_common.bls_django import HttpJsonOkResponse, HttpJsonResponse, HttpJsonResponse
from cc.apps.content.course_states import ActiveInUse, ActiveAssign, Active
from cc.apps.content.models import Segment, CourseGroup, Course
from cc.apps.management.models import UserProfile
from cc.apps.management.models import OneClickLinkToken
from cc.apps.tracking.models import TrackingEvent, active_modules_with_track_ratio, ScormActivityDetails, active_modules_with_track_ratio_sorted_by_last_event, TrackingEventService
from django.db import models as db_models
from django.db.models import Q
from cc.apps.tracking.utils import progress_formatter

from datetime import datetime

import urllib

from cc.libs.plato_common import decorators

logger = logging.getLogger("tracking")

@csrf_exempt
@http_decorators.require_POST
def create_event(request):
    """Handles event creation. If an event is a regular one a pair of START - END is created. Next time, if an event_id is given
    an update of END event is performed.

    :param request: POST JSON Request

    Return values:
    - 200 if event is created
    - 405 if request method is not POST
    """

    token = request.GET.get('token')
    one_click_link_token = None
    if token:
        try:
            one_click_link_token = OneClickLinkToken.objects.get(token=token)
        except OneClickLinkToken.DoesNotExist, e:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        
        if one_click_link_token.expired:
            return render(request,
                    'registration/login.html', {"ocl_expired": True})
    if one_click_link_token:
        loaded_user = one_click_link_token.user
    else:
        loaded_user = request.user

    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    is_scorm = "is_scorm" in data and bool(data["is_scorm"])
    is_update_end_event = "parent_event_id" in data
    is_user = "user_id" in data
    pg_nr = data.get('page_number', '')
    
    addr_list = request.META.get('HTTP_X_FORWARDED_FOR')
    if addr_list:
        client_ip = addr_list.split(',')[-1].strip()
    else:
        client_ip = request.META.get('REMOTE_ADDR', None)


    if is_scorm:
       if is_user:
           user = get_object_or_404(User, pk=data["user_id"])
       else:
           user = get_object_or_404(User, pk=loaded_user.id)
       segment = get_object_or_404(Segment, pk=data["segment_id"])
       _set_in_use_state_if_not_set_yet(segment.course)

       event = TrackingEvent.objects.create(segment=segment,
                                             participant=user,
                                             event_type=TrackingEvent.START_EVENT_TYPE, is_scorm=is_scorm)
       event.save()

       end_event = TrackingEvent.objects.create(segment=segment,
                                             participant=user,
                                             event_type=TrackingEvent.END_EVENT_TYPE,
                                             is_scorm=is_scorm,
                                             lesson_status=data["lesson_status"] if "lessons_status" in data else None,
                                             score_max=data["score_max"] if "score_max" in data else None,
                                             score_min=data["score_min"] if "score_min" in data else None,
                                             score_raw=data["score_raw"] if "score_raw" in data else None,
                                             client_ip = client_ip,
                                             parent_event=event)
       end_event.save()
    else:
        segment = get_object_or_404(Segment, pk=data["segment_id"])

        if not is_update_end_event:
            _set_in_use_state_if_not_set_yet(segment.course)

            event = TrackingEvent.objects.create(segment=segment,
                                         participant=get_object_or_404(User, pk=loaded_user.id),
                                         event_type=TrackingEvent.START_EVENT_TYPE, is_scorm=False,
                                         client_ip = client_ip)
            event.save()
            if pg_nr:
                page_event = TrackingEvent.objects.create(segment=segment,
                                            participant=get_object_or_404(User,
                                                pk=loaded_user.id),
                                            event_type=TrackingEvent.PAGE_EVENT_TYPE,
                                            is_scorm=False, parent_event=event,
                                            page_number=pg_nr,
                                            client_ip = client_ip)
                page_event.save()

            end_event = TrackingEvent.objects.create(segment=segment,
                                        participant=get_object_or_404(User,
                                            pk=loaded_user.id),
                                        event_type=TrackingEvent.END_EVENT_TYPE,
                                        is_scorm=False, parent_event=event,
                                        client_ip = client_ip)
            end_event.save()
        else:
            event = get_object_or_404(TrackingEvent, parent_event=data["parent_event_id"], event_type=TrackingEvent.END_EVENT_TYPE)
            event.created_on = datetime.now()
            if not (data["lesson_status"] == ""):
                event.lesson_status = data['lesson_status']

            try:
                params = urllib.urlencode({'user_id': event.participant_id, 'segment_id': segment.id, 'package_id': segment.file.key})
                url_file = urllib.urlopen((settings.SCORM_PLAYER_READER_URL + "?%s") % params)
                if url_file.getcode() == 200:
                    json_response = url_file.read()
                    if json_response:
                        try:
                            io = StringIO.StringIO(json_response)
                            scorm_status = json.load(io)
                            event.lesson_status = 'completed'
                            event.scorm_status = scorm_status["cmi.core.lesson_status"] if "cmi.core.lesson_status" in scorm_status else 'not attempted'
                            if "cmi.core.score.max" in scorm_status:
                                score_max = scorm_status["cmi.core.score.max"]
                                if score_max:
                                    event.score_max = score_max
                                else:
                                    event.score_max = 0
                            if "cmi.core.score.min" in scorm_status:
                                score_min = scorm_status["cmi.core.score.min"]
                                if score_min:
                                    event.score_min = score_min
                                else:
                                    event.score_min = 0
                            if "cmi.core.score.raw" in scorm_status:
                                score_raw = scorm_status["cmi.core.score.raw"]
                                if score_raw:
                                    event.score_raw = score_raw
                                else:
                                    event.score_raw = 0
                        except ValueError:
                            event.score_max = 0
                            event.score_min = 0
                            event.score_raw = 0
                            logger.error('Error parsing JSON data returned from scorm player.')


                result, message = scorm_activity_details(event.id)
                if not result:
                    logger.error(message)

            except IOError:
                logger.error('Problems while reading scorm data')

            event.save()
            if data.get('event_type', '')==TrackingEvent.PAGE_EVENT_TYPE:
                page_event = TrackingEvent.objects.create(segment=segment,
                                            participant=get_object_or_404(User,
                                                pk=loaded_user.id),
                                            event_type=TrackingEvent.PAGE_EVENT_TYPE,
                                            is_scorm=False,
                                            parent_event=get_object_or_404(
                                                TrackingEvent,
                                                pk=data['parent_event_id']),
                                            page_number=pg_nr,
                                            client_ip = client_ip)
                page_event.save()
    return HttpJsonResponse({'status': 'OK', "event_id": event.id})

@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def user_page_progress(request, end_event_id):
    """ user_page_progress

        Handles preparing the screen for detail page progress

        :params request: Request
        :params end_event_id: id of the finished event
    """
    def _get_duration(current, prev):
        delta = current - prev
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (hours, minutes, seconds)

    end_event = TrackingEvent.objects.get(pk=end_event_id)
    page_events = TrackingEvent.objects.filter(
                        parent_event=end_event.parent_event,
                        event_type=TrackingEvent.PAGE_EVENT_TYPE)
    tracking_list = []
    prev_id = None
    prev_time = None
    i = 0
    for event in page_events:
        track = {
            'id': event.id,
            'page':event.page_number,
            'date': event.created_on,}
        if prev_time:
            tracking_list[i-1]['duration'] = '%02d:%02d:%02d'%\
                    _get_duration(event.created_on, prev_time)
        i += 1
        prev_time = event.created_on
        tracking_list.append(track)
            
    delta = end_event.created_on - prev_time
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    tracking_list[len(tracking_list)-1]['duration'] = '%02d:%02d:%02d'%\
                    _get_duration(end_event.created_on, prev_time)
    return render(request,
                              'assignments/dialogs/user_page_progress.html',
                              {'tracks': tracking_list})

def _set_in_use_state_if_not_set_yet(course):
    if course.state_code == ActiveAssign.CODE:
        course.get_state().act("work_done")

@csrf_exempt
@http_decorators.require_POST
def update_scorm_event(request):
    """Handles scorm event update.

    :param request: POST JSON Request

    Return values:
    - 200 if event is created
    - 405 if request method is not POST
    """

    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    is_user = "user_id" in data
    if is_user:
        user = get_object_or_404(User, pk=data["user_id"])
    else:
        user = get_object_or_404(User, pk=request.user.id)

    event = TrackingEvent.objects.get(parent_event=data["event_id"], participant=user)

    event.lesson_status = data["lesson_status"]
    event.score_raw = data["score_raw"]
    event.score_max = data["score_max"]
    event.score_min = data["score_min"]
    event.save()
    return HttpJsonOkResponse()

@http_decorators.require_GET
def modules_with_tracking_ratio(request, group_id):
    """Returns modules for user with tracking ratio

    :param request: GET Request.
    :param group_id: id of the group for which data should be returned

    Return values:
    - 200 and JSON list with all courses for user and his group
    - 405 if request method is not GET
    """

    return bls_django.HttpJsonResponse(active_modules_with_track_ratio(request.user.id, group_id))


@http_decorators.require_GET
def segment_history(request, course_id, segment_id):
    """Returns segment history list ordered desc by create date

    :param request: GET Request.
    :param course_id: id of the course
    :param segment_id: id of the segment

    Return values:
    - 200 and JSON list with history for segment for course and participated user
    - 405 if request method is not GET
    """

    result = []
    previous = None
    for event in TrackingEvent.objects.filter(participant=request.user.id, segment__course=course_id, segment__id=segment_id):
        if previous == None:
            previous = event
        elif event.event_type == TrackingEvent.END_EVENT_TYPE and previous.event_type == TrackingEvent.START_EVENT_TYPE:
            timedelta = (event.created_on - previous.created_on)
            duration = timedelta.days*24*60*60 + timedelta.seconds
            result.append({"created_on": str(event.created_on), "duration": duration})
            previous = None
        elif event.event_type == TrackingEvent.START_EVENT_TYPE and previous.event_type == TrackingEvent.START_EVENT_TYPE:
            result.append({"created_on": str(previous.created_on), "duration": "NOT_FINISHED"})
            previous = event
        else:
            logger.warn("Inconsitent state of tracking info for user %d, course %d and segment %d"
                        % (request.user.id, course_id, segment_id))

    return bls_django.HttpJsonResponse(list(reversed(result)))

def report_tracking(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)
    group = get_object_or_404(Group, pk=report.group_id)

    group_data = {}
    group_data[group] = {}
    group_data[group]['id'] = group.id
    group_data[group]['courses']= group.course_set.annotate(
        segments_count=db_models.aggregates.Count("segment")).filter(
        ~db_models.query_utils.Q(segments_count = 0)).filter(
        state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE))

    group_data[group]['users_data'] = {}

    for user in group.user_set.filter(userprofile__role=UserProfile.ROLE_USER):
        if (group in owner_groups):
            mods = active_modules_with_track_ratio(user.id, group.id)
            for row in mods:
                row['ratio'] = progress_formatter(row['ratio'])
            group_data[group]['users_data'][user] = mods

    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    # First column empty
    module_names = ['']
    if request.GET.get('show_header', ''):
        modules = group_data[group]['courses']
        ratios = group_data[group]['users_data']
        for module in modules:
            module_names.append(module.title)
        writer.writerow(module_names)

    users = group_data[group]['users_data']
    for user in users:
        ratios = group_data[group]['users_data'][user]
        ratio_string = []
        ratio_string.append(user.first_name + ' ' + user.last_name)
        for ratio in ratios:
            ratio_string.append(str(ratio['ratio']))
        writer.writerow(ratio_string)

    return reports.get_csv('tracking.csv', result)

def _get_modules_data(user_id, group_id, course_id, owner_id, owner_groups):
    data = {}
    if user_id:
        user = User.objects.get(pk=user_id)
        data[user] = Course.objects.filter(coursegroup__group__user=user, coursegroup__group__in=owner_groups,
                                               state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()
    elif group_id:
        users = Group.objects.get(id=group_id).user_set.filter(userprofile__role=UserProfile.ROLE_USER)
        for user in users:
            data[user] = Course.objects.filter(coursegroup__group__user=user,
                                               coursegroup__group__in=owner_groups,
                                               state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()
    elif course_id:
        course = Course.objects.get(pk=course_id)
        for group in course.groups.filter(id__in=owner_groups):
            for user in group.user_set.filter(userprofile__role=UserProfile.ROLE_USER):
                data[user] = [course]
    return data

def _get_modules_usage_data(user_id, group_id, course_id, owner_id, owner_groups):
    data = {}
    if user_id:
        user = User.objects.get(pk=user_id)
        data[user] = Course.objects.filter(coursegroup__group__user=user, coursegroup__group__in=owner_groups,
                                               state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()
    elif group_id:
        courses_list = list(Course.objects.filter(groups=group_id,
                                               state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)))
        for user in Group.objects.get(id=group_id).user_set.filter(userprofile__role=UserProfile.ROLE_USER):
            data[user] = courses_list

    elif course_id:
        course = Course.objects.get(pk=course_id)
        for group in course.groups.filter(id__in=owner_groups):
            for user in group.user_set.filter(userprofile__role=UserProfile.ROLE_USER):
                data[user] = [course]
    return data

def modules_usage(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)
    data = _get_modules_data(report.user_id, report.group_id, report.course_id, report.owner_id, owner_groups)

    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    date_from = report.date_from if report.date_from else datetime.min
    date_to = report.date_to if report.date_to else datetime.max
    for user in data:
        for module in data[user]:
            segments = reports.get_tracking(user, module, date_from, date_to)

            modules_names = []
            if report.user_id:
                modules_names = [module.title]
            elif report.course_id:
                modules_names = [user.first_name + ' ' + user.last_name]
            elif report.group_id:
                modules_names = [user.first_name + ' ' + user.last_name + ' - ' + module.title]

            hours = 0
            minutes = 0
            seconds = 0

            for key, segment in segments.items():
                for tracking in segment['tracking']:
                    hours += int(tracking['duration'].split(":")[0])
                    minutes += int(tracking['duration'].split(":")[1])
                    seconds += int(tracking['duration'].split(":")[2])
            modules_names.append('%02d:%02d:%02d'%(reports.calculate_time(hours, minutes, seconds)))
            writer.writerow(modules_names)

    return reports.get_csv('modules_usage.csv', result)

def total_time(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)
    data = _get_modules_data(report.user_id, report.group_id, report.course_id, report.owner_id, owner_groups)

    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    date_from = report.date_from if report.date_from else datetime.min
    date_to = report.date_to if report.date_to else datetime.max
    for user in data:
        modules_names = [user.first_name + ' ' + user.last_name]

        hours = 0
        minutes = 0
        seconds = 0
        for module in data[user]:
            segments = reports.get_tracking(user, module, date_from, date_to)
            for key, segment in segments.items():
                for tracking in segment['tracking']:
                    hours += int(tracking['duration'].split(":")[0])
                    minutes += int(tracking['duration'].split(":")[1])
                    seconds += int(tracking['duration'].split(":")[2])

        modules_names.append('%02d:%02d:%02d'%(reports.calculate_time(hours, minutes, seconds)))
        writer.writerow(modules_names)

    return reports.get_csv('total_time.csv', result)

def user_progress(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)

    users = []
    if report.user_id:
        users = User.objects.filter(pk=report.user_id, groups__in=owner_groups).distinct()
    elif report.group_id:
        users = User.objects.filter(groups__id__contains=report.group_id,
                                    groups__in=owner_groups,
                                    userprofile__role=UserProfile.ROLE_USER).distinct()

    course = get_object_or_404(Course, pk=report.course_id)

    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    date_from = report.date_from if report.date_from else datetime.min
    date_to = report.date_to if report.date_to else datetime.max
    for user in users:
        segments = reports.get_tracking(user, course, date_from, date_to)
        if request.GET.get('show_header', ''):
            modules_names = ['']
            for key, segment in segments.items():
                modules_names.append(segment['segment'].file.title)
            writer.writerow(modules_names)

        times = [user.first_name + ' ' + user.last_name]
        for key, segment in segments.items():
            hours = 0
            minutes = 0
            seconds = 0

            tracking = {}

            for tracking in segment['tracking']:
                hours += int(tracking['duration'].split(":")[0])
                minutes += int(tracking['duration'].split(":")[1])
                seconds += int(tracking['duration'].split(":")[2])

            hours, minutes, seconds = (reports.calculate_time(hours, minutes, seconds))

            if (request.GET.get('show_scorm', '') and 'result' in tracking):
                times.append('%02d:%02d:%02d / %s'%(hours, minutes, seconds, tracking['result']))
            else:
                times.append('%02d:%02d:%02d'%(reports.calculate_time(hours, minutes, seconds)))

        writer.writerow(times)
    return reports.get_csv('user_progress.csv', result)

def dropped_modules(request):
    return


def scorm_activity_details(tracking_id):

    try:
        tracking = TrackingEvent.objects.get(pk=tracking_id)
    except TrackingEvent.DoesNotExist:
        return False, 'Tracking event (%s) does not exist.'%(tracking_id)


    params = urllib.urlencode({'user_id': tracking.participant.id, 'segment_id': tracking.segment.id, 'package_id': tracking.segment.file.key, 'results': '1'})
    url_file = urllib.urlopen((settings.SCORM_PLAYER_READER_URL + "?%s") % params)
    try:
        if url_file.getcode() == 200:
            json_response = url_file.read()
            scorm_results = json.loads(json_response)

            for result in scorm_results:
                scorm_activity = ScormActivityDetails(segment=tracking.segment,
                                                             user=tracking.participant,
                                                             tracking=tracking,
                                                             name=result['id'],
                                                             result=result['result'],
                                                             student_response=result['student_response'],
                                                             type=result['type'])
                scorm_activity.save()
    except Exception, e:
        return False, 'Error saving scorm activity details: %s'%(str(e))
    else:
        return True, 'OK'

def course_to_continue(request):
    for course in active_modules_with_track_ratio_sorted_by_last_event(request.user.id):
        if course["ratio"] != 1.0:
            segment = _choose_segment(request.user, course)
            if segment:
                return HttpJsonResponse(segment)

    raise Http404('No course to continue.')

def _choose_segment(user, course):
    segments = TrackingEventService().segments(user.id, course["id"])
    for idx, segment in enumerate(segments):
        if not segment.is_learnt and idx == 0:
            if not TrackingEvent.objects.filter(segment=segment, event_type="END", participant=user):
                return
            else:
                return {"course_id": course["id"], "segment_id": segment.id}
        elif not segment.is_learnt and idx > 0 :
            return {"course_id": course["id"], "segment_id": segment.id}
    return

