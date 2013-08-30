# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Liebek <bartosz.liebek@blstream.com>
#     Bartosz Oler <bartosz.oler@blstream.com>
#

import calendar, datetime, json, os, urllib, urlparse, StringIO

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.db.models import Sum
from django.utils.html import conditional_escape
from django.utils.translation import ugettext
from elementtree import SimpleXMLWriter
import django, time

from content import models


def _get_language_name(language_code):
    language = dict(settings.LANGUAGES).get(language_code)
    if not language:
        language = ugettext("Unspecified")
    return language

def serialize_course(course, user, tracking, ocl_token=None):
    groups_can_be_assigned = list(course.groups_can_be_assigned_to.values_list('id', flat=True))
    groups = list(auth_models.Group.objects.all().values_list('id', flat=True))
    if len(groups) == len(groups_can_be_assigned):
        groups_can_be_assigned.append(-2) # for "assign to --All-- groups"

    module = {
        'version': 1,
        'meta': {
            'id': course.id,
            'ownerId': course.owner.id,
            'ownerName': str(course.owner),
            'title': conditional_escape(course.title),
            'objective': conditional_escape(course.objective),
            'completion_msg': course.completion_msg,
            'created_on': ts_to_unix(course.created_on),
            'updated_on': ts_to_unix(course.updated_on),
            'published_on': ts_to_unix(course.published_on),
            'deactivated_on': ts_to_unix(course.deactivated_on),
            'expires_on': date_to_unix(course.expires_on),
            'language': course.language,
            'language_name': _get_language_name(course.language),
            'state': course.get_state().name(),
            'state_code': course.get_state().code(),
            'groups_names': list(course.groups.values_list('name', flat=True)),
            'groups_ids_can_be_assigned_to': str(groups_can_be_assigned),
            'available_actions': str(course.get_valid_actions()).replace("'", "\""),
            'allow_download': course.allow_download,
            'allow_skipping': course.allow_skipping,
            'show_sign_off': getattr(settings, 'SIGN_OFF_ON_MODULE', False),
            'sign_off_required': course.sign_off_required,
            'duration': models.Course.objects.filter(id=course.id).annotate(duration=Sum('segment__file__duration')).all()[0].duration
        },
        'track0': [],
        'track1': [],
        }
    for segment in course.segment_set.select_related():
        is_learnt = tracking.segmentIsLearnt(user.id, segment.id)
        download_url = segment.download_url
        if ocl_token:
            download_url += '?token=' + ocl_token

        entry = {
            'id': segment.file.id,
            'title': conditional_escape(segment.file.title),
            'type': segment.file.type,
            'thumbnail_url': segment.file.thumbnail_url,
            'preview_url': segment.file.preview_url,
            'created_on': ts_to_unix(segment.file.created_on),
            'expires_on': date_to_unix(segment.file.expires_on),
            'duration': segment.file.duration,
            'url': segment.get_view_url(user),
            'start': segment.start,
            'end': segment.end,
            'segment_id': segment.id,
            'is_learnt': is_learnt,
            'allow_downloading': segment.file.is_downloadable and course.allow_download and segment.file.status == models.File.STATUS_AVAILABLE, 
            'download_url': download_url,
            'pages_num': segment.file.pages_num,
            'allow_skipping': course.allow_skipping,
            'sign_off_required': getattr(settings, 'SIGN_OFF_ON_MODULE', False) and course.sign_off_required,
            }
        if segment.playback_mode:
            # TODO: Do not use get_playback_mode_display() as it is aimed for
            # user display, not machine processing and may change.
            entry['playback_mode'] = segment.get_playback_mode_display()

        module['track%d' % segment.track].append(entry)
    return module

def serialize_course_xml(course, user):
    output = StringIO.StringIO()
    tree = SimpleXMLWriter.XMLWriter(output, encoding='utf8')

    root = tree.start('module_descr', {'version': '1'})
    tree.start('meta')
    tree.element('id', str(course.id))
    tree.element('ownerId', str(course.owner.id))
    tree.element('ownerName', str(course.owner))
    tree.element('title', course.title)
    tree.element('objective', course.objective)
    tree.element('created_on', str(ts_to_unix(course.created_on)))
    tree.element('updated_on', str(ts_to_unix(course.updated_on)))
    tree.element('published_on', str(ts_to_unix(course.published_on)))
    tree.element('deactivated_on', str(ts_to_unix(course.deactivated_on)))
    tree.element('expires_on', str(date_to_unix(course.expires_on)))
    tree.element('language', course.language)
    tree.element('language_name', _get_language_name(course.language))
    tree.element('state', course.get_state().name())
    tree.element('state_code', str(course.get_state().code()))
    tree.element('groups_names', str(list(course.groups.values_list('name', flat=True))))
    tree.element('groups_ids_can_be_assigned_to', str(list(course.groups_can_be_assigned_to.values_list('id', flat=True))))
    tree.element("available_actions", str(course.get_valid_actions()))
    tree.element('allow_download', str(course.allow_download))
    tree.element('allow_skipping', str(course.allow_skipping))
    tree.element('show_sign_off', str(getattr(settings, 'SIGN_OFF_ON_MODULE', False)))
    tree.element('sign_off_required', str(course.sign_off_required))
    tree.element('duration', str(models.Course.objects.filter(id=course.id).annotate(duration=Sum('segment__file__duration')).all()[0].duration))
    tree.end()

    tracks = {}
    for segment in course.segment_set.select_related():
        tracks.setdefault(segment.track, []).append(segment)

    for n, segments in tracks.iteritems():
        track = tree.start('track', {'number': str(n)})
        for segment in segments:
            attribs = {
                'id': str(segment.file.id),
                'type': str(segment.file.type),
                'thumbnail_url': str(segment.file.thumbnail_url),
                'preview_url': str(segment.file.preview_url),
                'created_on': str(ts_to_unix(segment.file.created_on)),
                'url': segment.get_view_url(user),
                'segment_id': str(segment.id),
                'blocked': str(int(segment.file.status != models.File.STATUS_AVAILABLE)),
                'pages_num': str(segment.file.pages_num),
                'allow_downloading': str(segment.file.is_downloadable and course.allow_download),
                'allow_skipping': str(course.allow_skipping),
                'sign_off_required': str(getattr(settings, 'SIGN_OFF_ON_MODULE', False) and course.sign_off_required)
            }
            if segment.file.duration is not None:
                attribs['duration'] = str(segment.file.duration)

            tree.start('entry', attribs)
            tree.element('title', segment.file.title)
            tree.element('position', start=str(segment.start), end=str(segment.end))

            if segment.playback_mode:
                # TODO: Do not use get_playback_mode_display() as it is aimed for
                # user display, not machine processing and may change.
                tree.element('playback_mode', segment.get_playback_mode_display())
            tree.end()
        tree.end()
    tree.close(root)
    return output.getvalue()


def date_to_unix(d):
    if d is None:
        return d
    ts = datetime.datetime(d.year, d.month, d.day)
    return ts_to_unix(ts)

def ts_to_unix(ts):
    if ts is None:
        return ts
    return time.mktime(ts.timetuple())

def serialize_collection(collection):
    result = {
        'meta': {
            'id': collection.id,
            'title': collection.name
        },
        'track0': []
    }
    for element in models.CollectionElem.objects.filter(collection=collection):
        entry = {
            'id': element.file.id,
            'title': conditional_escape(element.file.title),
            'type': element.file.type,
            'thumbnail_url': element.file.thumbnail_url,
            'created_on': ts_to_unix(element.file.created_on),
            'expires_on': date_to_unix(element.file.expires_on),
            'duration': element.file.duration,
            'element_id': element.id,
            'allow_downloading': element.file.is_downloadable,
            'download_url': element.file.download_url
            }
        result['track0'].append(entry)
    
    return result



# vim: set et sw=4 ts=4 sts=4 tw=78:
