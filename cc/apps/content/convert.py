from django.conf import settings

from . import models
from cc.libs import utils

import os
import shutil
import subprocess
import tempfile


class ConversionError(Exception):
    pass


class BaseConverter(object):
    def __init__(self, file, storage, logger):
        self._file = file
        self._storage = storage
        self._logger = logger

    def convert(self):
        try:
            self._initialize()
            self._convert()
        except Exception, e:
            # Catch all exceptions as we want to process all errors in the
            # converters.
            self._file.status = models.File.STATUS_INVALID
            self._file.save()
            raise ConversionError(e)
        finally:
            self._finalize()

        self._file.status = models.File.STATUS_AVAILABLE
        self._file.save()
        self._logger.info('Successfully converted file %r.' % (self._file,))

    def _get_command(self):
        raise NotImplementedError()

    def _convert(self):
        try:
            self._run_command(self._get_command())
        except utils.CommandError, e:
            self._logger.error(
                'Conversion of file.id=%d from %s has failed '
                '(retcode = %d). %s' % (
                    self._file.id, self._get_src_path(), e.code, e.stdout
                    )
            )

    def _initialize(self):
        pass

    def _finalize(self):
        pass

    def _file_convertable(self):
        _, _, ext = self._file.orig_filename.rpartition('.')
        if ext.lower() not in models.CONVERSION_EXCLUSIONS:
            return True
        return False

    def _gen_tmp_path(self, suffix=None):
        root = self._storage.path(settings.CONTENT_UPLOADED_DIR)
        if suffix:
            fd, path = tempfile.mkstemp(suffix=suffix, dir=root)
        else:
            fd, path = tempfile.mkstemp(dir=root)
        os.close(fd)
        return path

    def _get_src_path(self):
        path = os.path.join(
            settings.CONTENT_UPLOADED_DIR,
            self._file.orig_file_path
        )
        return self._storage.path(path)

    def _get_dst_path(self):
        path = os.path.join(
            settings.CONTENT_AVAILABLE_DIR,
            self._file.conv_file_path
        )
        return self._storage.path(path)

    def _run_command(self, cmd, cwd=None):

        p = subprocess.Popen(
            cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,close_fds=True, cwd=cwd)
        # for win
        # p = subprocess.Popen(
        #     cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell = True)
        stdout, _ = p.communicate()
        if p.returncode != 0:
            raise utils.CommandError(cmd, p.returncode, stdout)

        return stdout


class BaseConverterWithTempDir(BaseConverter):
    def _initialize(self):
        super(BaseConverterWithTempDir, self)._initialize()
        root = self._storage.path(settings.CONTENT_UPLOADED_DIR)

        self._tmp = tempfile.mkdtemp(dir=root)


    def _finalize(self):
        super(BaseConverterWithTempDir, self)._finalize()

        try:


            shutil.move(self._tmp, self._get_dst_path())
            os.chmod(
                self._get_dst_path(), settings.FILE_UPLOAD_PERMISSIONS_DIRS
            )
        except OSError as e:
            try:
                shutil.rmtree(self._tmp)
            except OSError as e:
                self._logger.error(
                    'Cannot remove temp dir "%s" after conversion of "%s": %s'
                    % (self._tmp, self._file, str(e))
                )

            raise ConversionError('Cannot rename "%s" to "%s": %s' % (
                self._tmp, self._get_dst_path(), str(e)))


class PDFConverter(BaseConverterWithTempDir):
    def _get_command(self):
        dst = os.path.join(self._tmp, '%d.png')
        quality = '-r{}'.format(settings.PDF_CONVERT_QUALITY)

        return [
            'mudraw', quality, '-o', dst, self._get_src_path()
        ]

    def _run_command(self, cmd, cwd=None):

        output = super(PDFConverter, self)._run_command(cmd, cwd)
        if output and output.startswith('Error'):
            raise ConversionError(
                'Error during conversion of a PDF file '
                '(file id: %d): "%s"' % (
                    self._file.id, output.splitlines()[0]
                )
            )

    def _convert_to_json(self):

        dst = os.path.join(self._tmp, 'pdf.json')

        super(PDFConverter, self)._run_command([
            'pdf2json', self._get_src_path(), '-enc', 'UTF-8',
            '-compress', '-split', '10', dst
        ])

    def _convert(self):
        super(PDFConverter, self)._convert()
        self._convert_to_json()


def register(type, _class):
    """Registers new converter for the given file type.

    :param type: Id of the file type.
    :param _class: Class impementing converter.

    :return: Previous converter class or None.
    """

    old = unregister(type)
    _converters[type] = _class
    return old


def unregister(type):
    return _converters.pop(type, None)


def get_converter(file, storage, logger):
    try:
        return _converters[file.type](file, storage, logger)
    except KeyError:
        raise ConversionError('Unsupported file type: "%s".' % (file.type,))


# Registry of converters.
_converters = {}

# Register default converters.
register(models.File.TYPE_PDF, PDFConverter)
