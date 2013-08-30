
from django.contrib.auth import models as auth_models
from django.db import models, connection
from django import http
from cc.apps.content.course_states import Active, ActiveAssign, ActiveInUse
from cc.apps.content.models import Segment, Course
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from cc.apps.content.models import File

class TrackingEvent(models.Model):

    START_EVENT_TYPE = "START"
    END_EVENT_TYPE = "END"
    PAGE_EVENT_TYPE = "PAGE"

    segment = models.ForeignKey(Segment)
    participant = models.ForeignKey(auth_models.User)
    created_on = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(_('event type'), max_length=50)
    is_scorm = models.BooleanField(_('is scorm'), default=False)
    score_min = models.FloatField(_('scorm min score'), null=True)
    score_raw = models.FloatField(_('scorm raw score'), null=True)
    score_max = models.FloatField(_('scorm max score'), null=True)
    lesson_status = models.CharField(_('lesson status'), max_length=50, null=True)
    parent_event = models.ForeignKey('self', null=True)
    scorm_status = models.CharField(_('scorm status'), max_length=50, null=True)
    client_ip = models.CharField(_('client ip'), max_length=41, null=True)
    page_number = models.IntegerField(_('page number'), null=True)

    class Meta:
        ordering = ('created_on',)

    def __unicode__(self):
        return str(self.segment)+'. Event: '+self.event_type

class TrackingEventService(object):
    
    def segments(self, user_id, course_id):
        learnt_segments = Segment.objects.filter(track=0,
                                                   course=course_id,
                                                   course__groups__user=user_id,
                                                   trackingevent__event_type=TrackingEvent.END_EVENT_TYPE,
                                                   trackingevent__lesson_status='completed',
                                                   trackingevent__participant=user_id)
        result = []
        for segment in Segment.objects.filter(track=0, course=course_id, course__groups__user=user_id).distinct():
            segment.is_learnt = len(learnt_segments.filter(id=segment.id)) > 0
            segment.available = True
            result.append(segment)
        return result
    
    def segmentIsLearnt(self, user_id, segment_id):
        segment = Segment.objects.filter(track=0,
                                           id=segment_id,
                                           course__groups__user=user_id,
                                           trackingevent__event_type=TrackingEvent.END_EVENT_TYPE,
                                           trackingevent__lesson_status='completed',
                                           trackingevent__participant=user_id)
        return len(segment) > 0

    def trackingHistory(self, segment_id, participant_id, date_from=datetime.min, date_to=datetime.max):
        events = TrackingEvent.objects.filter(segment__id=segment_id, participant=participant_id)
        tracking_list = []
        start_date = None
        is_paging = False
        for event in events:
            if event.event_type == TrackingEvent.START_EVENT_TYPE:
                start_date = event.created_on
                start_event_id = event.id
            elif event.event_type == TrackingEvent.PAGE_EVENT_TYPE:
                is_paging = True
            elif event.event_type == TrackingEvent.END_EVENT_TYPE:
                end_date = event.created_on

                if start_date != None:
                    delta = end_date - start_date
    
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
    
                    tracking_element = {
                        'id': event.id,
                        'date':start_date,
                        'duration': '%02d:%02d:%02d'%(hours,minutes,seconds),
                        'result': None,
                        'is_paging': is_paging,
                        'client_ip': event.client_ip
                        }
                    if event.is_scorm:
                        tracking_element['result'] = '(%d/%d/%d) %s'%(event.score_min if event.score_min else 0,
                                                                      event.score_raw if event.score_raw else 0,
                                                                      event.score_max if event.score_max else 0,
                                                                      event.scorm_status if event.scorm_status else '')
                    if ((seconds > 0 or minutes > 0 or hours > 0) or \
                        (event.score_min or event.score_raw or event.score_max or event.lesson_status)) and (date_from <= start_date <= date_to):   
                        tracking_list.append(tracking_element)
                is_paging = False
        return tracking_list


def segments_count(courses_with_learnt_segments, course_id):
    course_outs = filter(lambda c: c.id==course_id, courses_with_learnt_segments)
    try:
        return course_outs[0].segments_count
    except IndexError, e:
        return 0
    #for course in courses_with_learnt_segments:
    #    if course.id == course_id:
    #        return course.segments_count
    #return 0

def active_modules_with_track_ratio_sorted_by_last_event(user_id):
    courses_with_all_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct segment.id) as segments_count,
        (SELECT max(created_on) FROM tracking_trackingevent as tte, content_segment as cs WHERE tte.segment_id = cs.id
        AND tte.event_type = 'END' AND tte.participant_id=%d AND cs.course_id=course_group.course_id AND tte.lesson_status = 'completed') as last_learn_date
        from cc.apps.content_coursegroup course_group
        join content_course course on course_group.course_id = course.id
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        and track = 0
        where user_group.user_id = %d
        and course.state_code in (2, 3, 4)
        group by course_group.course_id
        order by last_learn_date DESC""" % (int(user_id), int(user_id)))

    courses_with_learnt_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct trackingevent.segment_id) as segments_count
        from cc.apps.content_coursegroup course_group
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        left join tracking_trackingevent trackingevent on trackingevent.segment_id = segment.id
            and trackingevent.event_type = 'END'
            and trackingevent.lesson_status = 'completed'
            and trackingevent.participant_id = %d
        where user_group.user_id = %d
        and track = 0
        group by course_group.course_id""" % (int(user_id), int(user_id)))

    result = []
    for course in courses_with_all_segments:
        result.append({
            "id": course.id,
            "ratio": (float(segments_count(courses_with_learnt_segments, course.id)) / float(course.segments_count))
        })
    return result


def _active_modules_with_track_ratio(user_id, group_id):
    courses_with_all_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct segment.id) as segments_count, 
        count(distinct tracking_event.client_ip) as used_ips
        from cc.apps.content_coursegroup course_group
        join content_course course on course_group.course_id = course.id
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
            and track = 0
        left join tracking_trackingevent tracking_event on tracking_event.segment_id = segment.id
        where user_group.user_id = %d
        and auth_group.id = %d
        and course.state_code in (2, 3, 4)
        group by course_group.course_id""" % (int(user_id), int(group_id)))

    courses_with_learnt_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct trackingevent.segment_id) as segments_count
        from cc.apps.content_coursegroup course_group
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        left join tracking_trackingevent trackingevent on trackingevent.segment_id = segment.id
            and trackingevent.event_type = 'END'
            and trackingevent.lesson_status = 'completed' 
            and trackingevent.participant_id = %d
        where user_group.user_id = %d
        and auth_group.id = %d
        and track = 0
        group by course_group.course_id""" % (int(user_id), int(user_id), int(group_id)))

    result = []
    #for course in courses_with_all_segments:
    def append_result(course):
        return {"id": course.id,
                "ip_count": course.used_ips,
                "ratio":(float(segments_count(courses_with_learnt_segments, course.id)) / float(course.segments_count))}
    result = map(append_result, courses_with_all_segments)
    
    return result


def _module_with_track_ratio(user_id, course_id):
    course = Course.objects.get(id=course_id)
    segment_count = Segment.objects.filter(course=course_id, track=0).count()
    course_with_learnt_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct trackingevent.segment_id) as segments_count
        from cc.apps.content_coursegroup course_group
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        left join tracking_trackingevent trackingevent on trackingevent.segment_id = segment.id
            and trackingevent.event_type = 'END'
            and trackingevent.lesson_status = 'completed' 
            and trackingevent.participant_id = %d
        where user_group.user_id = %d
        and course_group.course_id = %d
        and track = 0
        group by course_group.course_id""" % (int(user_id), int(user_id), int(course_id)))
    if segment_count > 0:
        return float(segments_count(course_with_learnt_segments, course.id)) / float(segment_count)
    else:
        return 0


def active_modules_with_track_ratio(user_id, group_id):
    courses_with_all_segments = Course.objects.raw("""
        select course_group.course_id as id,
            count(distinct tracking_event.client_ip) as used_ips
        from cc.apps.content_coursegroup course_group
        join content_course course
            on course_group.course_id = course.id
        join auth_group auth_group
            on auth_group.id = course_group.group_id
        join auth_user_groups user_group
            on user_group.group_id = course_group.group_id
        join content_segment segment
            on segment.course_id = course_group.course_id
            and track = 0
        left join tracking_trackingevent tracking_event
            on tracking_event.segment_id = segment.id
        where user_group.user_id = %d
            and auth_group.id = %d
            and course.state_code in (2, 3, 4)
        group by course_group.course_id""" % (int(user_id), int(group_id)))

    result = []
    for course in courses_with_all_segments:
        result.append({
            "id": course.id,
            "ip_count": course.used_ips,
            "ratio": module_with_track_ratio(user_id, course.id)
        })
    return result


def module_with_track_ratio(user_id, course_id):
    segment_count = Segment.objects.filter(course=course_id, track=0).count()

    params = (int(user_id), int(user_id), int(course_id))
    learnt_segments = Course.objects.raw("""
        SELECT course_group.course_id AS id,
            trackingevent.segment_id AS segment_id
        FROM content_coursegroup course_group
        JOIN auth_group auth_group
            ON auth_group.id = course_group.group_id
        JOIN auth_user_groups user_group
            ON user_group.group_id = course_group.group_id
        JOIN content_segment segment
            ON segment.course_id = course_group.course_id
        LEFT JOIN tracking_trackingevent trackingevent
            ON trackingevent.segment_id = segment.id
            AND trackingevent.event_type = 'END'
            AND trackingevent.lesson_status = 'completed'
            AND trackingevent.participant_id = %s
        WHERE user_group.user_id = %s
        AND course_group.course_id = %s
        AND track = 0
        GROUP BY course_group.course_id, trackingevent.segment_id""", params)

    learnt_segs = []  # list of learnt segments IDs
    for s in learnt_segments:
        if s.segment_id > 0:
            learnt_segs.append(str(s.segment_id))
    total_learnt = len(learnt_segs)

    additional_condition = ''
    if total_learnt > 0:
        additional_condition = ('AND trackingevent.segment_id NOT IN (%s)'
                                % ', '.join(learnt_segs))
    params = (
        int(user_id),
        int(user_id),
        int(course_id),
        additional_condition,
        File.TYPE_VIDEO
    )
    learning_segments = Course.objects.raw("""
        SELECT course_group.course_id AS id,
            trackingevent.segment_id AS segment_id,
            MAX(trackingevent.page_number) AS page_number,
            file.pages_num AS total_pages,
            file.type AS file_type
        FROM content_coursegroup course_group
        JOIN auth_group auth_group
            ON auth_group.id = course_group.group_id
        JOIN auth_user_groups user_group
            ON user_group.group_id = course_group.group_id
        JOIN content_segment segment
            ON segment.course_id = course_group.course_id
        JOIN content_file file
            ON file.id = segment.file_id
        LEFT JOIN tracking_trackingevent trackingevent
            ON trackingevent.segment_id = segment.id
        WHERE user_group.user_id = %d
            AND trackingevent.participant_id = %d
            AND course_group.course_id = %d
            AND track = 0
            %s
            AND (trackingevent.event_type = 'PAGE'
                OR (trackingevent.event_type = 'START' AND file.type = %d))
        GROUP BY course_group.course_id, trackingevent.segment_id,
            file.pages_num, file.type""" % params)

    learning_segs = []  # list of learning segment ratios
    total_learning_ratio = 0
    for s in learning_segments:
        if s.segment_id > 0:
            # mark video file as complete right after starting
            if s.file_type == File.TYPE_VIDEO:
                ratio = 1
            else:
                ratio = float(s.page_number) / float(s.total_pages)
            total_learning_ratio += ratio
            learning_segs.append(ratio)
    total_learning = len(learning_segs)

    if total_learnt > 0 or total_learning > 0:
        return float(total_learnt + total_learning_ratio) / float(segment_count)
    else:
        return 0


class ScormActivityDetails(models.Model):

    segment = models.ForeignKey(Segment)
    user = models.ForeignKey(auth_models.User)
    tracking = models.ForeignKey(TrackingEvent)
    name = models.CharField(max_length=100)
    result = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    student_response = models.CharField(max_length=100)

    class Meta:
        ordering = ('tracking', 'tracking__created_on')
