# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Various utilities for the content app.
"""

import random, subprocess

from django.conf import settings

from cc.apps.content import baseconv


BASE62_CONV = baseconv.BaseConverter(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz')


class UnsupportedFileTypeError(Exception):
    def __init__(self, ext):
        self.ext = ext

    def __str__(self):
        return 'Files with extension "%s" are not supported.' % (self.ext,)

class CommandError(Exception):
    def __init__(self, cmd=None, code=None, stdout=None, stderr=None):
        self.cmd = cmd
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return 'Command [%s] has failed with code: %d' % (self.cmd, self.code)


def get_rand_bytes_as_hex(n):
    """Returns string of n random bytes encoded as hex.

    Mind that because of the hex encoding length of the returned string is ``2 * n``.

    :param n: Number of random bytes.
    :type n: ``int``

    :return: String of random bytes.
    :rtype: ``str``
    """

    return ''.join([chr(random.randint(0, 255)) for _ in xrange(n)]).encode('hex')


def gen_file_key():
    """Generates random file key.

    :return: File key, length is between 1 - 22 bytes.
    :rtype: ``str``
    """

    # 62**22 - 1 (full 22 base-62 digits) > 2**128
    n = random.randint(1, 62 ** 22 - 1)
    return BASE62_CONV.encode(n)


def gen_file_sub_key():
    """Generates random file sub key.

    :return: File sub key, length is between 1 - 5 bytes.
    :rtype: ``str``
    """

    n = random.randint(1, 62 ** 5 - 1)
    return BASE62_CONV.encode(n)

def gen_ocl_token():
    """Generates random ocl token.

    :return: token, length equals 30 bytes.
    :rtype: ``str``
    """

    return BASE62_CONV.encode(random.randint(62 ** 29 - 1, 62 ** 30 - 1))


