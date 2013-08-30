# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Django command which generates random sample files.
"""


import random, re
from optparse import make_option

from django.contrib.webdesign import lorem_ipsum
from django.core.management.base import BaseCommand, CommandError

from content import models


class Command(BaseCommand):
    help = 'Adds random files to the database.'

    option_list = BaseCommand.option_list + (
        make_option('--files-min',
            action='store',
            type=int,
            default=3,
            help='Minimum number of files per type.'),
        make_option('--files-max',
            action='store',
            type=int,
            default=8,
            help='Maximum number of files per type.'),
        )

    _type_to_exts = {
        models.File.TYPE_IMAGE: models.IMAGE_FILES,
        models.File.TYPE_AUDIO: models.AUDIO_FILES,
        models.File.TYPE_VIDEO: models.VIDEO_FILES,
        models.File.TYPE_PLAIN: models.PLAIN_FILES,
        models.File.TYPE_MSDOC: models.MSDOC_FILES,
        models.File.TYPE_MSPPT: models.MSPPT_FILES,
        models.File.TYPE_SCORM: models.SCORM_FILES,
        models.File.TYPE_PDF: models.PDF_FILES,
        }

    def handle(self, *args, **options):
        for tid, tname in models.File.TYPES:
            n = random.randint(options['files_min'], options['files_max'])
            print 'generating %d files of type %s' % (n, tname)
            for i in xrange(n):
                title = sentence()

                status = models.File.STATUS_AVAILABLE
                if random.random() < 0.4:
                    status = models.File.STATUS_UPLOADED

                f = models.File(
                    title=title,
                    status=status,
                    type=tid,
                    orig_filename=self._build_filename(tid, title))
                print repr(f)
                f.save()

    def _build_filename(self, type, title):
        fn = re.sub('[^a-zA-Z]', '', title)[:200]
        ext = random.choice(list(self._type_to_exts[type]))
        return '%s.%s' % (fn, ext)




def sentence():
    sections = [lorem_ipsum.words(random.randint(2, 4), common=False)
                    for i in range(random.randint(1, 2))]
    s = u', '.join(sections)
    return u'%s%s%s' % (s[0].upper(), s[1:], random.choice('?.'))


# vim: set et sw=4 ts=4 sts=4 tw=78:
