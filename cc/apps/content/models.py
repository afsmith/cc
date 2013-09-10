from django.conf import settings
from django.contrib.auth import models as auth_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cc.apps.accounts.models import CUser

import json
import os
import urllib
import urlparse
import utils
import course_states
import type_specifiers

"""
Django models related to content handled by the system.

These models represent various business types needed to create and use courses.
"""

PLAIN_FILES = frozenset([
    'txt',
])

IMAGE_FILES = frozenset([
    'jpg',
    'jpeg',
    'png',
    'gif',
])

AUDIO_FILES = frozenset([
    'aac',
    'aiff',
    'au',
    'fla',
    'flac',
    'm4a',
    'mp2',
    'mp3',
    'ra',
    'wav',
    'wma',
])

VIDEO_FILES = frozenset([
    'avi',
    'flv',
    'm4v',
    'mov',
    'mpg',
    'mpeg',
    'wmv',
])

MSDOC_FILES = frozenset([
    'doc',
    'odt',
])

MSPPT_FILES = frozenset([
    'ppt',
    'odp',
])

SCORM_FILES = frozenset([
    'zip',
])

PDF_FILES = frozenset([
    'pdf',
])

HTML_FILES = frozenset([
    'html',
    'htm',
])

MULTITYPE_FILES = frozenset([
    'ogg',
    'rm',
    'mp4',
])

CONVERSION_EXCLUSIONS = frozenset([
    'html',
    'htm',
    'jpg',
    'jpeg',
    'gif',
])


class ModuleDescrError(Exception):
    def __init__(self, reason, field=None):
        self.reason = reason
        self.field = field

    def __str__(self):
        return self.reason % {'field': self.field}


class File(models.Model):
    """Represents single file managed by the system.

    Files are building blocks of courses.
    """

    TYPE_PLAIN = 10
    TYPE_IMAGE = 20
    TYPE_AUDIO = 30
    TYPE_VIDEO = 40
    TYPE_MSDOC = 50
    TYPE_MSPPT = 60
    TYPE_SCORM = 70
    TYPE_PDF = 80
    TYPE_HTML = 90
    TYPES = (
        (TYPE_PLAIN, _('plain')),
        (TYPE_IMAGE, _('image')),
        (TYPE_AUDIO, _('audio')),
        (TYPE_VIDEO, _('video')),
        (TYPE_MSDOC, _('doc')),
        (TYPE_MSPPT, _('ppt')),
        (TYPE_SCORM, _('scorm')),
        (TYPE_PDF, _('pdf')),
        (TYPE_HTML, _('html'))
    )

    STATUS_UPLOADED = 10
    STATUS_INVALID = 20
    STATUS_AVAILABLE = 30
    STATUS_REMOVED = 40
    STATUS_EXPIRED = 50
    STATUSES = (
        (STATUS_UPLOADED, _('uploaded')),
        (STATUS_AVAILABLE, _('available')),
        (STATUS_REMOVED, _('removed'))
    )

    title = models.CharField(_('Name'), max_length=150)
    type = models.IntegerField(_('Type'), choices=TYPES)
    # In theory (according to an article on a Wikipedia) file name shouldn't
    # be longer than 255 chars.
    orig_filename = models.CharField(_('Original File Name'), max_length=255)
    status = models.IntegerField(
        _('Status'),
        choices=STATUSES, default=STATUS_UPLOADED
    )
    # Unique identifier of the file.
    key = models.CharField(_('Key'), max_length=22, unique=True,
        default=utils.gen_file_key)

    subkey_orig = models.CharField(_('Original Sub Key'), max_length=5,
        default=utils.gen_file_sub_key)
    subkey_conv = models.CharField(_('Converted Sub Key'), max_length=5,
        default=utils.gen_file_sub_key)
    subkey_thumbnail = models.CharField(_('Thumbnail Sub Key'), max_length=5,
        default=utils.gen_file_sub_key)
    subkey_preview = models.CharField(_('Preview Sub Key'), max_length=5,
        default=utils.gen_file_sub_key)

    created_on = models.DateTimeField(_('Created on'), auto_now_add=True)
    updated_on = models.DateTimeField(_('Updated on'), auto_now=True)
    expires_on = models.DateField(_('Expiration date'), null=True)
    delete_expired = models.BooleanField(_('Delete file after expiration'), default=False)
    is_downloadable = models.BooleanField(_('Allow downloading'), default=True)
    duration = models.IntegerField(_('Duration'), null=True)
    note = models.CharField(_('Note'), max_length=400, null=True)
    # Currently the longest language code in settings.LANGUAGES has 7 chars.
    language = models.CharField(_('Language'), choices=settings.LANGUAGES, max_length=7)
    groups = models.ManyToManyField(auth_models.Group)
    owner = models.ForeignKey(CUser, null=True)
    pages_num = models.IntegerField(_('Number of content pages'), default=0)

    is_removed = models.BooleanField(_('Content is removed'), default=False)

    @classmethod
    def type_from_name(cls, name):
        """Guesses file type based on the file name.

        :param name: File name.
        :type name: ``str``

        :return: File's type identifier.
        :rtype: ``int``

        :raises: UnsupportedFileTypeError -- if cannot map file name to type identifier.
        """
        _, _, ext = name.rpartition('.')
        ext = ext.lower()
        if ext in PLAIN_FILES:
            return cls.TYPE_PLAIN
        elif ext in IMAGE_FILES:
            return cls.TYPE_IMAGE
        elif ext in AUDIO_FILES:
            return cls.TYPE_AUDIO
        elif ext in VIDEO_FILES:
            return cls.TYPE_VIDEO
        elif ext in MSDOC_FILES:
            return cls.TYPE_MSDOC
        elif ext in MSPPT_FILES:
            return cls.TYPE_MSPPT
        elif ext in SCORM_FILES:
            return cls.TYPE_SCORM
        elif ext in PDF_FILES:
            return cls.TYPE_PDF
        elif ext in HTML_FILES:
            return cls.TYPE_HTML
        elif ext in MULTITYPE_FILES:
            return type_specifiers.get_specifier(ext, name, File).get_type()
        else:
            raise utils.UnsupportedFileTypeError(ext)

    @classmethod
    def is_supported_file(cls, name):
        _, _, ext = name.rpartition('.')
        ext = ext.lower()
        all_types = (list(PLAIN_FILES) +
                     list(IMAGE_FILES) +
                     list(AUDIO_FILES) +
                     list(VIDEO_FILES) +
                     list(MSDOC_FILES) +
                     list(MSPPT_FILES) +
                     list(SCORM_FILES) +
                     list(PDF_FILES) +
                     list(HTML_FILES) +
                     list(MULTITYPE_FILES))

        if ext in all_types:
            return True
        else:
            return False

    @property
    def original_url(self):
        """Returns URL to the original version of the file.

        :return: URL
        :rtype: ``str``
        """
        path = os.path.join(settings.CONTENT_AVAILABLE_DIR, self.orig_file_path)
        return urlparse.urljoin(settings.MEDIA_URL, path)

    @property
    def download_url(self):
        """Returns URL to the original version of the file with original name

        :return: URL
        :rtype: ``str``
        """
        return "/content/file/%d/download/" % self.pk

    @property
    def view_url(self):
        """Returns URL to the converted version of the file.

        In case of Scorm files, returned URL points to the scorm player.

        :return: URL
        :rtype: ``str``
        """

        if self.type == self.TYPE_SCORM:
            qs = urllib.urlencode({
                'scormPackageID': self.key,
                'tree': 'true',
                'userID': 'fakeuser',
                'segmentID': 'preview',
            })

            return settings.SCORM_PLAYER_ENDPOINT + '?' + qs
        elif self.orig_filename.rpartition('.')[2].lower() in CONVERSION_EXCLUSIONS:
            path = os.path.join(settings.CONTENT_UPLOADED_DIR, self.orig_file_path)
            return urlparse.urljoin(settings.MEDIA_URL, path)
        else:
            path = os.path.join(settings.CONTENT_AVAILABLE_DIR, self.conv_file_path)
            return urlparse.urljoin(settings.MEDIA_URL, path)

    @property
    def ext(self):
        """Returns file extension which is appropriate for this file type.

        :return: Extension.
        :rtype: ``str``
        """

        return self.orig_filename.rpartition('.')[2]

    @property
    def orig_file_path(self):
        """Returns relative path to the original version of the file.

        :rtype: `str`
        """
        return '%s_%s.%s' % (self.key, self.subkey_orig, self.ext)

    @property
    def conv_file_path(self):
        """Returns relative path to the converted version of the file.

        :rtype: `str`
        """
        type_to_ext = {
            self.TYPE_PLAIN: 'txt',
            self.TYPE_IMAGE: 'png',
            self.TYPE_AUDIO: 'mp3',
            self.TYPE_VIDEO: 'flv',
            self.TYPE_MSDOC: 'doc',
            self.TYPE_MSPPT: 'ppt',
            self.TYPE_SCORM: 'zip',
            self.TYPE_PDF: 'pdf',
            self.TYPE_HTML: 'html',
        }
        ext = type_to_ext[self.type]
        return '%s_%s.%s' % (self.key, self.subkey_conv, ext)

    @property
    def thumbnail_file_path(self):
        return '%s_%s.%s' % (self.key, self.subkey_thumbnail, 'jpg')

    @property
    def thumbnail_url(self):
        path = os.path.join(settings.CONTENT_THUMBNAILS_DIR, self.thumbnail_file_path)
        return urlparse.urljoin(settings.MEDIA_URL, path)

    @property
    def preview_file_path(self):
        return '%s_%s.%s' % (self.key, self.subkey_preview, 'jpg')

    @property
    def preview_url(self):
        path = os.path.join(settings.CONTENT_PREVIEWS_DIR, self.preview_file_path)
        return urlparse.urljoin(settings.MEDIA_URL, path)

    def __repr__(self):
        return u'<File[%s]: %s; type=%s; status=%s>' % (self.id, repr(self.title),
            self.get_type_display(), self.get_status_display())

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('created_on',)


class Course(models.Model):
    """Represents course assembled from several Files.

    Files can belong to one of two tracks.
    """

    groups = models.ManyToManyField(
        auth_models.Group, through='content.CourseGroup'
    )
    groups_can_be_assigned_to = models.ManyToManyField(
        auth_models.Group, 
        through="content.CourseGroupCanBeAssignedTo",
        related_name="course_can_assign"
    )
    title = models.CharField(_('Title'), max_length=150)
    objective = models.TextField(_('Objective'), blank=True)
    completion_msg = models.TextField(
        _('Goodbye message'), blank=True, default='Module finished', null=True
    )
    state_code = models.IntegerField(
        _('State code'), default=course_states.Draft.CODE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    expires_on = models.DateField(_('Expiration date'), null=True)
    published_on = models.DateTimeField(_('Publish date'), null=True)
    deactivated_on = models.DateTimeField(_('Deactivated date'), null=True)
    active = models.BooleanField(default=False)
    language = models.CharField(
        _('Language'), choices=settings.LANGUAGES, max_length=7
    )
    owner = models.ForeignKey(CUser, null=True)
    allow_download = models.BooleanField(_('Allow downloads'), default=False)
    allow_skipping = models.BooleanField(_('Allow skipping'), default=False)
    sign_off_required = models.BooleanField(
        _('Sign off required'), default=False
    )

    def __unicode__(self):
        return self.title

    def is_assigned_to_all(self):
        return len(self.groups.all()) == len(auth_models.Group.objects.all())

    def get_state(self):
        states = [course_states.Draft(self),
                  course_states.Active(self),
                  course_states.ActiveAssign(self),
                  course_states.ActiveInUse(self),
                  course_states.Deactivated(self),
                  course_states.DeactivatedUsed(self),
                  course_states.Removed(self)]
        for state in states:
            if state.code() == self.state_code:
                return state
        raise course_states.InvalidStateCodeError

    def get_valid_actions(self):
        result = []
        for action in self.get_state().actions():
            result.append(action._name)
        return result

    def is_available_for_user(self, user):
        if self.state_code not in (course_states.ActiveAssign.CODE,
                                   course_states.ActiveInUse.CODE):
            return False

        return self.groups.filter(pk__in=user.groups.all()).exists()

    class Meta:
        ordering = ('created_on',)


def get_segments_with_available_flag(segments_with_learnt_flag):
    result = []
    unfinished = 0
    for segment in segments_with_learnt_flag:
        if segment.is_learnt:
            segment.available = True
        elif unfinished == 0:
            unfinished = 1
            segment.available = True
        else:
            segment.available = False
        result.append(segment)
    return result


class Segment(models.Model):
    """File assigned to one of course's tracks.
    """

    TRACKS = (
        (0, '#0'),
        (1, '#1'),
    )

    MODE_ONCE = 10
    MODE_REPEAT = 20

    MODES = (
        (MODE_ONCE, 'once'),
        (MODE_REPEAT, 'repeat'),
    )

    file = models.ForeignKey(File)
    course = models.ForeignKey(Course)

    track = models.IntegerField(_('Track'), choices=TRACKS)
    start = models.IntegerField(_('Start offset'))
    end = models.IntegerField(_('End offset'))
    playback_mode = models.IntegerField(_('Playback mode'), choices=MODES,
        null=True, blank=True)

    def __unicode__(self):
        return u'%s in %s' % (self.file, self.course)

    class Meta:
        ordering = ('course', 'start', 'track')

    def get_view_url(self, user):
        """Returns view URL for the given user.

        :param user: User for who the URL should be provided.
        """
        if self.file.type == File.TYPE_SCORM and user.get_profile().is_user:
            url = urlparse.urlsplit(self.file.view_url)
            qs = urlparse.parse_qs(url.query)
            qs['segmentID'] = self.id
            qs['userID'] = user.id
            url = urlparse.urlunsplit((
                url.scheme,
                url.netloc,
                url.path,
                urllib.urlencode(qs, doseq=True),
                url.fragment))

            return url
        else:
            return self.file.view_url

    @property
    def download_url(self):
        """Returns URL to the original version of the file with original name.
        This url actions counts also download times for user per segment.

        :return: URL
        :rtype: ``str``
        """
        return "/content/segment/%d/download/" % self.pk


class DownloadEvent(models.Model):
    """Stores download events
    """

    segment = models.ForeignKey(Segment)
    user = models.ForeignKey(CUser)
    download_time = models.DateTimeField(auto_now_add=True)


class CourseGroupCanBeAssignedTo(models.Model):
    """Stores associations between modules and their groups can be assigned to.
    """
    group = models.ForeignKey(auth_models.Group)
    course = models.ForeignKey(Course)


class CourseGroup(models.Model):
    """Stores associations between groups and their modules.
    """

    group = models.ForeignKey(auth_models.Group)
    course = models.ForeignKey(Course)
    assigner = models.ForeignKey(CUser, null=True)
    assigned_on = models.DateField()


class CourseUser(models.Model):
    """Stores associations between user and their modules.
    """

    user = models.ForeignKey(CUser)
    course = models.ForeignKey(Course)
    sign_off = models.BooleanField(_('Sign off module'), default=False)
    sign_off_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%s, %s %s" % (
            self.course.title, self.user.first_name, self.user.last_name
        )


class ModuleDescrParser(object):
    supported_versions = (1,)
    mode_ext_to_int = {
        'repeat': Segment.MODE_REPEAT,
        'once': Segment.MODE_ONCE,
    }

    def __init__(self, descr, owner):
        self._descr = descr
        self._course = None
        self._owner = owner

    def parse(self):
        try:
            descr = json.loads(self._descr)
        except ValueError, e:
            raise ModuleDescrError('Cannot parse description as JSON: %s' % str(e))

        if 'version' not in descr:
            raise ModuleDescrError('The %(field)s field is missing.',
                field='version')

        try:
            version = int(descr['version'])
        except TypeError:
            raise ModuleDescrError('Invalid version of the module description.',
                field='version')

        if version not in self.supported_versions:
            raise ModuleDescrError('Unsupported version of the module description.',
                field='version')

        if 'meta' not in descr:
            raise ModuleDescrError('The %(field)s field is missing.',
                field='meta')

        if 'id' in descr['meta']:
            value = descr['meta']['id']
            if (not isinstance(value, (int, long))) or (value != abs(value)):
                raise ModuleDescrError('The %(field)s field has invalid value.',
                    field='meta.id')
            course = self._get_course(value)
        else:
            course = self._get_course()

        if 'title' not in descr['meta']:
            raise ModuleDescrError('The %(field)s field is missing.',
                field='meta.title')

        if not descr['meta']['title'].strip():
            raise ModuleDescrError('The %(field)s field cannot be empty.',
                field='meta.title')
        course.title = descr['meta']['title'].strip()

        if 'objective' not in descr['meta']:
            raise ModuleDescrError('The %(field)s field is missing.',
                field='meta.objective')

        course.objective = descr['meta']['objective'].strip()

        course.owner = self._owner
        course.save()

        self._parse_track('track0', descr)
        self._parse_track('track1', descr)

        course.groups_can_be_assigned_to.clear()
        self._add_default_can_be_assigned_to_groups()

        return course.id

    def _add_default_can_be_assigned_to_groups(self):
        for group in self._intersect_groups(self._get_course().segment_set.all()):
            CourseGroupCanBeAssignedTo(course=self._get_course(), group=group).save()

    def _intersect_groups(self, segments):
        if segments.count() == 0:
            return {}
        else:
            if self._owner.get_profile().is_superadmin:
                result = set(segments[0].file.groups.all())
            else:
                result = set(self._owner.groups.all())
            for segment in segments:
                result &= set(segment.file.groups.all())
            return result

    def _parse_track(self, track, descr):
        if track not in descr:
            raise ModuleDescrError('The %(field)s field is missing.',
                field=track)

        entries = descr[track]

        for i, entry in enumerate(entries):
            id = self._get_entry_field_int(entry, 'id', i, track)
            start = self._get_entry_field_int(entry, 'start', i, track)
            end = self._get_entry_field_int(entry, 'end', i, track)
            if start > end:
                raise ModuleDescrError('The end field %(field)s has value lower than the start field.',
                    field='%s.%d.%s' % (track, i, 'end'))
            mode = self._get_playback_mode(entry, i, track)
            self._add_segment(id, track, start, end, mode)

    def _get_entry_field_int(self, entry, name, n, track):
        if name not in entry:
            raise ModuleDescrError('The %(field)s field is missing.',
                field='%s.%d.%s' % (track, n, name))

        value = entry[name]
        if (not isinstance(value, (int, long))) or (value != abs(value)):
            raise ModuleDescrError('The %(field)s field has invalid value.',
                field='%s.%d.%s' % (track, n, name))

        return value

    def _get_playback_mode(self, entry, n, track):
        field = '%s.%d.%s' % (track, n, 'playback_mode')
        if 'playback_mode' in entry:
            if track != 'track1':
                raise ModuleDescrError('The %(field)s field is not allowed', field=field)
            mode = entry['playback_mode']
            if mode not in ('once', 'repeat'):
                raise ModuleDescrError('Invalid playback mode on field %(field)s', field=field)
            return mode
        else:
            if track != 'track0':
                raise ModuleDescrError('The %(field)s field is missing', field=field)

    def _get_course(self, id=None):
        if self._course:
            return self._course

        if id is None:
            self._course = Course()
        else:
            try:
                self._course = Course.objects.get(pk=id)
            except Course.DoesNotExist:
                raise ModuleDescrError(
                    'Course with the given id (field: %(field)s) does not exist',
                    field='meta.id')
            self._course.segment_set.all().delete()

        return self._course

    def _add_segment(self, file_id, track, start, end, playback_mode):
        if playback_mode is not None:
            playback_mode = self.mode_ext_to_int[playback_mode]

        track_id = int(track[-1])
        f = File.objects.get(pk=file_id)
        s = Segment(
            course=self._get_course(),
            file=f,
            track=track_id,
            start=start,
            end=end,
            playback_mode=playback_mode,
        )
        s.save()
