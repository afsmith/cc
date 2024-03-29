from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cc.apps.accounts.models import CUser
from cc.libs import utils

from os.path import join, abspath
import urlparse
import type_specifiers


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
    '''
    Represents single file managed by the system.
    '''
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

    type = models.IntegerField(_('Type'), choices=TYPES)
    # In theory (according to an article on a Wikipedia) file name shouldn't
    # be longer than 255 chars.
    orig_filename = models.CharField(_('Original File Name'), max_length=255)
    status = models.IntegerField(
        _('Status'),
        choices=STATUSES, default=STATUS_UPLOADED
    )
    # Unique identifier of the file.
    key = models.CharField(
        _('Key'), max_length=22, unique=True, default=utils.gen_file_key
    )

    subkey_orig = models.CharField(
        _('Original Sub Key'), max_length=5, default=utils.gen_file_sub_key
    )
    subkey_conv = models.CharField(
        _('Converted Sub Key'), max_length=5, default=utils.gen_file_sub_key
    )
    subkey_thumbnail = models.CharField(
        _('Thumbnail Sub Key'), max_length=5, default=utils.gen_file_sub_key
    )
    subkey_preview = models.CharField(
        _('Preview Sub Key'), max_length=5, default=utils.gen_file_sub_key
    )
    created_on = models.DateTimeField(_('Created on'), auto_now_add=True)
    updated_on = models.DateTimeField(_('Updated on'), auto_now=True)
    owner = models.ForeignKey(CUser, null=True)
    pages_num = models.IntegerField(_('Number of content pages'), default=0)

    link_text = models.CharField(_('Link text'), max_length=150, blank=True)
    index = models.IntegerField(default=1)

    @classmethod
    def type_from_name(cls, name):
        """Guesses file type based on the file name.

        :param name: File name.
        :type name: ``str``

        :return: File's type identifier.
        :rtype: ``int``

        :raises: UnsupportedFileTypeError
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
        all_types = (
            list(IMAGE_FILES) +
            list(PDF_FILES)
        )
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
        path = join(settings.CONTENT_UPLOADED_DIR, self.orig_file_path)
        return urlparse.urljoin(settings.MEDIA_URL, path)

    @property
    def view_url(self):
        """Returns URL to the converted version of the file.

        :return: URL
        :rtype: ``str``
        """
        path = join(settings.CONTENT_AVAILABLE_DIR, self.conv_file_path)
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
    def orig_file_abspath(self):
        path = join(settings.CONTENT_UPLOADED_DIR, self.orig_file_path)
        return abspath(join(settings.MEDIA_ROOT, path))

    @property
    def conv_file_path(self):
        """Returns relative path to the converted version of the file.

        :rtype: `str`
        """
        '''type_to_ext = {
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
        return '%s_%s.%s' % (self.key, self.subkey_conv, ext)'''

        return '{}_{}'.format(self.key, self.subkey_conv)

    @property
    def thumbnail_file_path(self):
        return '%s_%s.%s' % (self.key, self.subkey_thumbnail, 'jpg')

    @property
    def preview_file_path(self):
        return '%s_%s.%s' % (self.key, self.subkey_preview, 'jpg')

    def __repr__(self):
        return u'<File[%s]: %s; type=%s; status=%s>' % (
            self.id,
            repr(self.orig_filename),
            self.get_type_display(), self.get_status_display()
        )

    def __unicode__(self):
        return self.orig_filename

    class Meta:
        ordering = ('created_on',)
