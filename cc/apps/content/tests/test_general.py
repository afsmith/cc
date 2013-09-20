from __future__ import absolute_import

from django.conf import settings
from django.core.files import storage
from django.core.urlresolvers import reverse

from cc.apps.content.models import File
from cc.apps.content import utils

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
        f.name = 'bar.jpg'
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
        response = c.post(self.url, {'file': f})
        print response
        f.close()
        self.assertEquals(File.objects.all().count(), 1)

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


class UtilsTest(ClientTestCase):
    """Tests utils from ``content.utils`` module.
    """

    def test_returned_string_is_exactly_twice_long_as_number_of_bytes(self):
        s = utils.get_rand_bytes_as_hex(5)
        self.assertEquals(len(s), 10)

        s = utils.get_rand_bytes_as_hex(200)
        self.assertEquals(len(s), 400)

    def test_returned_string_is_encoded_as_hex(self):
        s = utils.get_rand_bytes_as_hex(100)
        try:
            int(s, 16)
        except ValueError:
            self.fail('String %s contains digits out of hex range.' % (s,))

    def test_gen_file_key_returns_string(self):
        key = utils.gen_file_key()
        self.assertTrue(isinstance(key, str))


'''
class DeleteExpiredTaskTest(ClientTestCase):
    fixtures = ('sample.json', 'test-course.json', 'test-tags.json',)

    def test_task_marks_deleted_content(self):
        files_count = File.objects.filter(expires_on__isnull = False,
                                                expires_on__lt = datetime.date.today(),
                                                is_removed = False).count()

        tasks.delete_expired_content()

        files_count_new = File.objects.filter(expires_on__isnull = False,
                                                     expires_on__lt = datetime.date.today(),
                                                     is_removed = False).count()

        self.assertTrue(files_count != files_count_new)
        self.assertEquals(files_count_new, 0)


    def test_task_deactivates_modules(self):
        active_modules = models.Course.objects.filter(segment__file__expires_on__lt = datetime.date.today(),
                                                      segment__file__is_removed = True,
                                                      active=True).count()
        self.assertEquals(active_modules, 0)


class ExceptionalConverter(convert.BaseConverter):
    class Exc(Exception):
        pass

    class File(object):
        status = None
        def save(self):
            pass

    def __init__(self, exc_in_initialize=True):
        self._file = self.File()
        self.exc_in_initialize = exc_in_initialize
        self.was_finalized = False

    def _initialize(self):
        if self.exc_in_initialize:
            raise self.Exc()

    def _convert(self):
        raise self.Exc()

    def _finalize(self):
        self.was_finalized = True


class FakeLogger(object):
    def __init__(self):
        self.logs = []

    def info(self, msg):
        self.logs.append(msg)

    def error(self, msg):
        self.logs.append(msg)


class FailingConverter(convert.BaseConverter):
    def _get_command(self):
        raise convert.ConversionError('Conversion has failed on purpose!')

class SuccessfulConverter(convert.BaseConverter):
    def _convert(self):
        pass

    def _create_thumbnail(self):
        pass


class ConvertTest(TestCase):
    fake_type = 31337

    def test_run_command_raises_exception_on_error(self):
        conv = convert.BaseConverter(None, None, None)
        self.assertRaises(utils.CommandError, conv._run_command, ['false'])

    def test_finalize_gets_called_on_exception_in_initialize(self):
        conv = ExceptionalConverter()
        try:
            conv.convert()
        except convert.ConversionError:
            pass

        self.assertTrue(conv.was_finalized)

    def test_no_converters_are_registered_with_our_unique_test_only_type(self):
        try:
            self.assertEquals(None, convert.register(self.fake_type, None))
        finally:
            convert.unregister(self.fake_type)

    def test_unregister_removes_converter(self):
        try:
            conv = object()
            convert.register(self.fake_type, conv)
            convert.unregister(self.fake_type)
            self.assertEquals(None, convert.register(self.fake_type, None))
        finally:
            convert.unregister(self.fake_type)

    def test_finalize_gets_called_on_exception_in_convert(self):
        conv = ExceptionalConverter(exc_in_initialize=False)
        try:
            conv.convert()
        except convert.ConversionError:
            pass

        self.assertTrue(conv.was_finalized)

    def test_register_returns_previous_converter(self):
        try:
            converter = object()
            # just to make sure we don't register converter for this magic number
            self.assertEquals(None, convert.register(self.fake_type, converter))

            self.assertEquals(converter, convert.register(self.fake_type, None))
        finally:
            convert.unregister(self.fake_type)

    def test_get_converter_for_unknown_type_raises_error(self):
        fake_file = FakeFile()
        fake_file.type = self.fake_type

        self.assertRaises(
            convert.ConversionError,
            convert.get_converter, fake_file, None, None)

    def test_failed_conversion_marks_file_as_invalid(self):
        file = self._create_file('foo.jpeg', File.TYPE_IMAGE)
        conv = FailingConverter(file, None, FakeLogger())
        self.assertRaises(
            convert.ConversionError,
            conv.convert)
        self.assertEquals(file.status, File.STATUS_INVALID)

    def test_successful_conversion_marks_file_as_available(self):
        file = self._create_file('foo.jpeg', File.TYPE_IMAGE)
        conv = SuccessfulConverter(file, None, FakeLogger())
        conv.convert()
        self.assertEquals(file.status, File.STATUS_AVAILABLE)

    def test_pdf_files_are_converted_using_mocked_command(self):
        file = self._create_file('foo.pdf', File.TYPE_PDF)

        from django.core.files import storage
        conv = convert.PDFConverter(file, storage.default_storage, FakeLogger())
        conv._convert_preview = lambda: None
        conv._convert_thumbnail = lambda: None
        conv.convert()
        self.assertEquals(file.status, File.STATUS_AVAILABLE)

    def test_can_recognize_errors_in_pdf_converter(self):
        file = self._create_file('foo.pdf', File.TYPE_PDF)
        # FAIL is a magic flag for mocked converter which causes it to fail
        # like the original converter (pdftohtml).
        file.subkey_orig = file.subkey_orig[-4] + 'FAIL'
        file.save()
        conv = convert.PDFConverter(file, storage.default_storage, FakeLogger())
        self.assertRaises(convert.ConversionError, conv.convert)
        self.assertEquals(file.status, File.STATUS_INVALID)

    def _create_file(self, name, type):
        file = File(orig_filename=name, type=type)
        file.save()
        return file

class VideoConverterTest(TestCase):

    fixtures = ('test-files.json',)

    def setUp(self):
        self.vc = VideoConverter(File.objects.get(id=1), FakeStorage(), None)
        self.vc._tmp = ["tmp.mp4", "tmp.webm", "tmp.ogv", "temp.flv"]

    def test_should_be_medium_if_there_is_no_config_entry(self):
        self.assertEquals(self.vc._get_command_medium_quality(), self.vc._get_command_flv())

    def test_should_return_same_command_for_high_quality(self):
        ConfigEntry(config_key=ConfigEntry.CONTENT_QUALITY_OF_CONTENT, config_val=ConfigEntry.QUALITY_TYPE_HIGH).save()
        self.assertEquals(self.vc._get_command_high_quality(), self.vc._get_command_flv())

    def test_should_return_same_command_for_medium_quality(self):
        ConfigEntry(config_key=ConfigEntry.CONTENT_QUALITY_OF_CONTENT, config_val=ConfigEntry.QUALITY_TYPE_MEDIUM).save()
        self.assertEquals(self.vc._get_command_medium_quality(), self.vc._get_command_flv())

    def test_should_return_same_command_for_low_quality(self):
        ConfigEntry(config_key=ConfigEntry.CONTENT_QUALITY_OF_CONTENT, config_val=ConfigEntry.QUALITY_TYPE_LOW).save()
        self.assertEquals(self.vc._get_command_low_quality(), self.vc._get_command_flv())

'''


