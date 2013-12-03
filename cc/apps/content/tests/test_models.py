from __future__ import absolute_import

from cc.apps.content.models import File
from cc.apps.content import utils

from cc.libs.test_utils import ClientTestCase


class FileModelTest(ClientTestCase):
    """Tests the File model.
    """

    def test_type_from_name_raises_exception_if_unknown_extension(self):
        try:
            File.type_from_name('foo.bah')
            self.fail('Exception UnsupportedFileTypeError not risen.')
        except utils.UnsupportedFileTypeError:
            pass

    def test_type_from_name_raises_exception_if_no_extension(self):
        try:
            File.type_from_name('foo')
            self.fail('Exception UnsupportedFileTypeError not risen.')
        except utils.UnsupportedFileTypeError:
            pass

    def test_type_from_name_raises_exception_if_no_extension_after_delimeter(self):
        try:
            File.type_from_name('foo.')
            self.fail('Exception UnsupportedFileTypeError not risen.')
        except utils.UnsupportedFileTypeError:
            pass

    def test_type_from_name_correctly_regognizes_uppercase_extension(self):
        type = File.type_from_name('foo.JPG')
        self.assertEquals(type, File.TYPE_IMAGE)

    def test_type_from_name_correctly_regognizes_lowercase_extension(self):
        type = File.type_from_name('foo.mp3')
        self.assertEquals(type, File.TYPE_AUDIO)

    def test_type_from_name_correctly_regognizes_mixedcase_extension(self):
        type = File.type_from_name('foo.JpEg')
        self.assertEquals(type, File.TYPE_IMAGE)

    def test_original_url_has_original_file_ext(self):
        f = File(type=File.TYPE_VIDEO, orig_filename='foo.bar')
        f.save()
        self.assertEquals(f.original_url.rpartition('.')[2], 'bar')
        f.delete()

    def test_original_url_has_key_instead_of_original_name(self):
        f = File(type=File.TYPE_VIDEO, orig_filename='foo.bar')
        f.save()
        key = f.original_url.rpartition('/')[2].partition('.')[0]
        self.assertEquals(key, '%s_%s' % (f.key, f.subkey_orig))
        f.delete()

    def test_ext_returns_extension_based_on_original_file_name(self):
        f = File(type=File.TYPE_VIDEO, orig_filename='foo.bar')
        self.assertEquals(f.ext, 'bar')
