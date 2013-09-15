from __future__ import absolute_import

from django.core.files import storage

from cc.apps.content.models import File
from cc.apps.content import utils

from cc.libs.test_utils import ClientTestCase

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
