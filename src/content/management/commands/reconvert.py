# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Django command for forcing re-conversion of already uploaded files.
"""


from django.core.management.base import BaseCommand, CommandError, LabelCommand

from content import models, tasks


class Command(LabelCommand):
    help = 'Triggers re-conversion of the specified file.'

    def handle_label(self, label, **options):
        try:
            file = models.File.objects.get(key=label)
        except models.File.DoesNotExist:
            print 'ERROR: File with the given key does not exist.'
        else:
            tasks.process_stored_file.delay(file)


# vim: set et sw=4 ts=4 sts=4 tw=78:
