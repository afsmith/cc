# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

"""Type specifiers for multitype files.
"""

import fnmatch, os, re, shutil, subprocess, tempfile, traceback

from cc.libs import utils

from django.conf import settings

_type_specifiers = {}

def get_specifier(file_ext, file_path, file_class):
    if file_ext in _type_specifiers.keys():
        return _type_specifiers[file_ext](file_ext, file_path, file_class)
    else:
        raise utils.UnsupportedFileTypeError(ext)

def add_specifier(file_ext, class_):
    _type_specifiers[file_ext] = class_


class FileTypeSpecifier(object):
    def __init__(self, file_ext, file_path, file_class):
        super(FileTypeSpecifier, self).__init__()
        self._file_ext = file_ext
        self._file_path = file_path
        self._file_class = file_class

    def get_type(self):
        pass

class AVTypeSpecifier(FileTypeSpecifier):

    def get_type(self):
        cmd = ['ffprobe', os.path.join(settings.MEDIA_ROOT, self._file_path)]
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            close_fds=True, cwd=None)
        stdout, _ = p.communicate()
        if p.returncode != 0:
            raise utils.CommandError(cmd, p.returncode, stdout)

        for line in stdout.splitlines():
            if re.search('Stream #\d+.\d+.*: Video:', line):
                return self._file_class.TYPE_VIDEO
        return self._file_class.TYPE_AUDIO



add_specifier('ogg', AVTypeSpecifier)
add_specifier('rm', AVTypeSpecifier)
add_specifier('mp4', AVTypeSpecifier)