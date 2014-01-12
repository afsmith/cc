from __future__ import absolute_import

from django.core.files import storage
from django.test import TestCase

from cc.apps.content.models import File
from cc.apps.content import convert
from cc.libs import utils
from .test_general import FakeFile


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

    def _create_file(self, name, type):
        file = File(orig_filename=name, type=type)
        file.save()
        return file
