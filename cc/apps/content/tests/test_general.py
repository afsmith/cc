from __future__ import absolute_import

from django.conf import settings
from django.core.files import storage
from django.core.urlresolvers import reverse

from cc.apps.content.models import File

from cc.libs import utils
from cc.libs.test_utils import ClientTestCase

import json
import StringIO


class FakeStorage(object):
    """Limited Django storage backend.
    """

    def __init__(self):
        self.last_filename = None
        self.last_buf = None

    def open(self, path, mode):
        self.last_filename = path.rpartition('/')[2]
        self.last_buf = FakeFile()
        return self.last_buf

    def path(self, path):
        return 'path'


class FakeFile(object):
    """Fake file returned from the storage backend.
    """

    def __init__(self):
        self.size = 0
        self.closed = False

    def write(self, s):
        self.size += len(s)

    def close(self):
        self.closed = True


class ImportFileTest(ClientTestCase):
    """Exercises import_file view.
    """
    fixtures = ['test-users-content.json']

    url = reverse('upload_file')

    def setUp(self):
        self._storage = FakeStorage()
        self._orig_storage = storage.default_storage
        storage.default_storage = self._storage
        self._FILE_UPLOAD_MAX_MEMORY_SIZE = settings.FILE_UPLOAD_MAX_MEMORY_SIZE

    def tearDown(self):
        storage.default_storage = self._orig_storage
        settings.FILE_UPLOAD_MAX_MEMORY_SIZE = self._FILE_UPLOAD_MAX_MEMORY_SIZE

    def _get_fh(self, size=1024):
        f = StringIO.StringIO('A' * size)
        f.name = 'bar.pdf'
        return f

    def test_get_method_not_allowed(self):
        c = self._get_client_admin()
        r = c.get(self.url)
        self.assertEquals(r.status_code, 405)

    def test_invalid_form_post_returns_form(self):
        c = self._get_client_admin()
        response = c.post(self.url)
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_on_post_file_is_required(self):
        c = self._get_client_admin()
        response = c.post(self.url, {})
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_upload_of_file_without_ext_results_in_error(self):
        c = self._get_client_admin()
        f = self._get_fh()
        f.name = 'no-extension-here'
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_upload_of_file_with_unknown_ext_results_in_error(self):
        c = self._get_client_admin()
        f = self._get_fh()
        f.name = 'foo.unknown-extension'
        response = c.post(self.url, {'file': f})
        f.close()
        data = json.loads(response.content)
        self.assertEquals(data['status'], "ERROR")

    def test_adds_imported_file_to_database(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        self.assertEquals(File.objects.all().count(), 1)

    def test_upload_file_returns_page_count(self):
        c = self._get_client_admin()
        f = self._get_fh()
        resp = c.post(self.url, {'file': f})
        json_resp = json.loads(resp.content)
        self.assertEquals(json_resp.get('page_count'), -1)
        f.close()

    #
    # I've disabled this test for now as we don't have any way to skip
    # conversion and it is eager (read: blocking) when tests are run.
    # That means there is no chance we can see files with UPLOADED status. -- BOL
    #
    def _test_new_files_are_in_uploaded_status(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f = File.objects.all()[0]
        self.assertEquals(f.status, File.STATUS_UPLOADED)

    def test_stores_original_filename_of_uploaded_files(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f2 = File.objects.all()[0]
        self.assertEquals(f2.orig_filename, f.name)

    def test_uploaded_files_get_assigned_unique_key(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f = File.objects.all()[0]
        self.assertTrue(isinstance(f.key, basestring))
        self.assertTrue(len(f.key))

    def test_stores_file_after_upload_using_key_and_ext(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        f2 = File.objects.all()[0]
        self.assertEquals(self._storage.last_filename, f2.orig_file_path)

    def test_writes_all_content_to_file(self):
        size = (1024 ** 2)
        c = self._get_client_admin()
        f = self._get_fh(size=size)
        c.post(self.url, {'file': f})
        f.close()
        self.assertEquals(self._storage.last_buf.size, size)

    def test_should_not_write_content_reached_max_upload_size(self):
        size = (1024 ** 2) * 11
        settings.FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 ** 2
        c = self._get_client_admin()
        f = self._get_fh(size=size)
        c.post(self.url, {'file': f})
        f.close()
        self.assertFalse(self._storage.last_buf)

    def test_closes_file_after_write(self):
        c = self._get_client_admin()
        f = self._get_fh()
        c.post(self.url, {'file': f})
        f.close()
        self.assertTrue(self._storage.last_buf.closed)
