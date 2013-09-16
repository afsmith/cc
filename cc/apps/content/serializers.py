import calendar, datetime, json, os, urllib, urlparse, StringIO

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.db.models import Sum
from django.utils.html import conditional_escape
from django.utils.translation import ugettext
import django, time

from . import models


def _get_language_name(language_code):
    language = dict(settings.LANGUAGES).get(language_code)
    if not language:
        language = ugettext("Unspecified")
    return language

def serialize_course(course, user, tracking=None, ocl_token=None):
    module = {
        'version': 1,
        'meta': {
            'id': course.id,
            'ownerId': course.owner.id,
            'ownerName': str(course.owner),
            'title': conditional_escape(course.title),
            'created_on': ts_to_unix(course.created_at),
            'updated_on': ts_to_unix(course.modified_at),
            'groups_names': course.group.name,
        },
        'track0': [],
    }
    for file in course.files.all():
        #is_learnt = tracking.segmentIsLearnt(user.id, segment.id)
        #download_url = segment.download_url
        #if ocl_token:
        #    download_url += '?token=' + ocl_token

        entry = {
            'id': file.id,
            'title': conditional_escape(file.title),
            'type': file.type,
            'thumbnail_url': file.thumbnail_url,
            'preview_url': file.preview_url,
            'created_on': ts_to_unix(file.created_on),
            'expires_on': date_to_unix(file.expires_on),
            'duration': file.duration,
            'url': file.view_url,
            #'start': segment.start,
            #'end': segment.end,
            #'segment_id': segment.id,
            #'is_learnt': is_learnt,
            #'allow_downloading': segment.file.is_downloadable and course.allow_download and segment.file.status == models.File.STATUS_AVAILABLE, 
            #'download_url': download_url,
            #'pages_num': file.pages_num,
            #'allow_skipping': course.allow_skipping,
            #'sign_off_required': getattr(settings, 'SIGN_OFF_ON_MODULE', False) and course.sign_off_required,
        }
        #if segment.playback_mode:
            # TODO: Do not use get_playback_mode_display() as it is aimed for
            # user display, not machine processing and may change.
            #entry['playback_mode'] = segment.get_playback_mode_display()

        module['track0'].append(entry)

    return module



def date_to_unix(d):
    if d is None:
        return d
    ts = datetime.datetime(d.year, d.month, d.day)
    return ts_to_unix(ts)

def ts_to_unix(ts):
    if ts is None:
        return ts
    return time.mktime(ts.timetuple())
