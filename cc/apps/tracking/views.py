
import json

from django import http
from cc.apps.accounts.models import CUser as User, Group
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