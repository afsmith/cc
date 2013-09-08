# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""Various utilities for Django.
"""


import os

from django import http
from django.core import serializers
from django.conf import settings
from django.db.models import query
from django.utils import simplejson
from django.test.simple import DjangoTestSuiteRunner


class HttpResponseCreated(http.HttpResponse):
    status_code = 201


class HttpJsonResponse(http.HttpResponse):
    """HTTP response with mime-type and caching siutable for JSON.
    """
    def __init__(self, object):
        if isinstance(object, query.QuerySet):
            content = serializers.serialize('json', object)
        else:
            content = simplejson.dumps(object)
        super(HttpJsonResponse, self).__init__(content, mimetype='application/json')
        self['Pragma'] = 'no cache'
        self['Cache-Control'] = 'no-cache, must-revalidate'


class HttpJsonOkResponse(HttpJsonResponse):
    def __init__(self):
        super(HttpJsonOkResponse, self).__init__({'status': 'OK'})


class CeleryTestRunner(DjangoTestSuiteRunner):
    """Test runner that forces CELERY_ALWAYS_EAGER.
    """
    def __init__(self, *args, **kwargs):
        super(CeleryTestRunner, self).__init__(*args, **kwargs)

    def setup_test_environment(self, **kwargs):
        super(CeleryTestRunner, self).setup_test_environment(**kwargs)
        settings.CELERY_ALWAYS_EAGER = True
        # Add mocked commands' dir as first on the search path.
        mocks = os.path.join(
            os.path.dirname(__file__), '..', '..', 'tools', 'mocks')
        os.environ['PATH'] = mocks + os.pathsep + os.environ['PATH']


'
