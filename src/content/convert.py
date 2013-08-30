# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""File format converters.
"""


import fnmatch, os, re, shutil, subprocess, tempfile, traceback
from xml.dom.minidom import parse

from django.conf import settings
from content.models import get_entry_val, ConfigEntry

import models, utils


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
                'Conversion of file.id=%d from %s has failed (retcode = %d). %s' % (
                    self._file.id, self._get_src_path(), e.code, e.stdout))

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
            fd, path = tempfile.mkstemp(suffix=suffix,dir=root)
        else:
            fd, path = tempfile.mkstemp(dir=root)
        os.close(fd)
        return path

    def _gen_miniature_path(self):
        root = self._storage.path(settings.CONTENT_UPLOADED_DIR)
        fd, path = tempfile.mkstemp(dir=root)
        os.close(fd)
        return path
    
    def _get_src_path(self):
        path = os.path.join(settings.CONTENT_UPLOADED_DIR, self._file.orig_file_path)
        return self._storage.path(path)

    def _get_dst_path(self):
        path = os.path.join(settings.CONTENT_AVAILABLE_DIR, self._file.conv_file_path)
        return self._storage.path(path)

    def _get_thumbnail_path(self):
        path = os.path.join(settings.CONTENT_THUMBNAILS_DIR, self._file.thumbnail_file_path)
        return self._storage.path(path)

    def _get_preview_path(self):
        path = os.path.join(settings.CONTENT_PREVIEWS_DIR, self._file.preview_file_path)
        return self._storage.path(path)

    def _run_command(self, cmd, cwd=None):
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            close_fds=True, cwd=cwd)
        stdout, _ = p.communicate()
        if p.returncode != 0:
            raise utils.CommandError(cmd, p.returncode, stdout)

        return stdout

class BaseConverterWithTempFile(BaseConverter):
    def _initialize(self):
        super(BaseConverterWithTempFile, self)._initialize()
        self._tmp = self._gen_tmp_path()

    def _finalize(self):
        super(BaseConverterWithTempFile, self)._finalize()

        if self._file_convertable():
            try:
                os.rename(self._tmp, self._get_dst_path())
                os.chmod(self._get_dst_path(), settings.FILE_UPLOAD_PERMISSIONS)
            except OSError as e:
                try:
                    os.unlink(self._tmp)
                except OSError as e2:
                    self._logger.error(
                        'Cannot unlink temp file "%s" after conversion of "%s": %s' % (
                        self._tmp, self._file, str(e2)))

                raise ConversionError('Cannot rename "%s" to "%s": %s' % (
                    self._tmp, self._get_dst_path(), str(e)))


class BaseConverterWithTempDir(BaseConverter):
    def _initialize(self):
        super(BaseConverterWithTempDir, self)._initialize()
        root = self._storage.path(settings.CONTENT_UPLOADED_DIR)
        self._tmp = tempfile.mkdtemp(dir=root)

    def _finalize(self):
        
        super(BaseConverterWithTempDir, self)._finalize()

        try:
            shutil.move(self._tmp, self._get_dst_path())
            os.chmod(self._get_dst_path(), settings.FILE_UPLOAD_PERMISSIONS_DIRS)
        except OSError as e:
            try:
                shutil.rmtree(self._tmp)
            except OSError as e:
                self._logger.error(
                    'Cannot remove temp dir "%s" after conversion of "%s": %s' % (
                    self._tmp, self._file, str(e)))

            raise ConversionError('Cannot rename "%s" to "%s": %s' % (
                self._tmp, self._get_dst_path(), str(e)))


class MediaConverter(BaseConverterWithTempFile):
    def _get_command_length(self):
        cmd = ['ffprobe', self._get_src_path()]
        return cmd

    def _get_length(self):
        output = super(MediaConverter, self)._run_command(self._get_command_length())
        print output
        matched = None
        result = 0
        for line in output.splitlines():
            if 'Duration:' in line:
                matched = re.search(r'Duration: (\d\d):(\d\d):\d\d.\d\d', line)
                break
        if matched:
            result = 60*int(matched.group(1)) + int(matched.group(2)) + 1
        return result
    
    def _finalize(self):
        if self._file.status == models.File.STATUS_INVALID:
            for tmp in self._tmp:
                os.unlink(tmp)
        elif self._file_convertable():
            try:
                dstPath, dstExt = os.path.splitext(self._get_dst_path())
                for tmp in self._tmp:
                    tmpPath, tmpExt = os.path.splitext(tmp)
                    tmpPath = dstPath + tmpExt
                    if os.path.exists(tmp):
                        os.rename(tmp, tmpPath)
                        os.chmod(tmpPath, settings.FILE_UPLOAD_PERMISSIONS)
            except OSError as e:
                try:
                    for tmp in self._tmp:
                        os.unlink(tmp)
                except OSError as e2:
                    self._logger.error(
                        'Cannot unlink temp file "%s" after conversion of "%s": %s' % (
                        self._tmp, self._file, str(e2)))

                raise ConversionError('Cannot rename "%s" to "%s": %s' % (
                    self._tmp, self._get_dst_path(), str(e)))

class ScormConverter(BaseConverter):
    """Imports given Scorm file to the Reload Scorm Player.
    """

    def _get_command(self):
        cmd = [
            'java', '-jar', settings.SCORM_IMPORTER,
            '-config-file=' + settings.SCORM_IMPORTER_CONF,
            '-package=' + self._get_src_path(),
            '-lesson-name=' + self._file.key]

        return cmd

    def _run_command(self, cmd):
        super(ScormConverter, self)._run_command(
            cmd, cwd=settings.SCORM_IMPORTER_BASE_DIR)

    def _get_package_path(self):
        dom = parse(settings.SCORM_IMPORTER_CONF)
        root_dir = courses_dir = ''
        for node in dom.getElementsByTagName('entry'):
            if node.getAttribute('key') == 'root.dir':
                root_dir = node.childNodes[0].nodeValue
            elif node.getAttribute('key') == 'coursepackage.dir':
                courses_dir = node.childNodes[0].nodeValue
        return os.path.join(root_dir, courses_dir, self._file.key)


    def _finalize(self):
        super(ScormConverter, self)._finalize()
        package_path = ''
        try:
            package_path = self._get_package_path()
            os.path.walk(package_path, self._chmodRecursive, settings.FILE_UPLOAD_PERMISSIONS_DIRS)
        except Exception, e:
            raise ConversionError('Cannot change permissions of "%s" to "%s": %s' % (
                package_path, settings.FILE_UPLOAD_PERMISSIONS_DIRS, str(e)))

    def _chmodRecursive(self, arg, dirname, fnames):
        os.chmod(dirname, arg)
        for file in fnames:
            os.chmod(os.path.join(dirname, file), arg)

class VideoConverter(MediaConverter):
    
    video_quality_params = {
        ConfigEntry.QUALITY_TYPE_HIGH: ['-b:v', '896k', '-ab', '64000', '-preset', 'slow'],
        ConfigEntry.QUALITY_TYPE_MEDIUM: ['-b:v', '640k', '-ab', '64000', '-preset', 'slow'],
        ConfigEntry.QUALITY_TYPE_LOW: ['-b:v', '512k', '-ab', '64000', '-preset', 'medium'],
    }
    
    def _initialize(self):
        self._tmp = list()
        for i in range(4):
            self._tmp.append(self._gen_tmp_path(''.join(['.',
                                ConfigEntry.CONTENT_VIDEO_FORMATS[i]])))

    def _get_command_high_quality(self):
        return [
            'ffmpeg', '-i', self._get_src_path(),
            '-f', 'flv', '-r', '25', '-mbd', '1', '-vf', 'scale=trunc(oh*a/2)*2:480', '-sameq',
            '-acodec', 'libmp3lame', '-ar', '22050', '-ab', '64000',
            '-y', self._tmp[3],
            ]

    def _get_command_medium_quality(self):
        return [
            'ffmpeg', '-i', self._get_src_path(),
            '-f', 'flv', '-r', '25', '-mbd', '1', '-vf', 'scale=trunc(oh*a/2)*2:480', '-qscale', '4',
            '-acodec', 'libmp3lame', '-ar', '22050', '-ab', '64000', '-y', self._tmp[3],
            ]

    def _get_command_low_quality(self):
        return [
            'ffmpeg', '-i', self._get_src_path(),
            '-f', 'flv', '-r', '25', '-mbd', '1', '-vf', 'scale=trunc(oh*a/2)*2:480',
            '-acodec', 'libmp3lame', '-ar', '22050', '-ab', '64000',
            '-vcodec', '-preset', 'medium', 'libx264', '-y', self._tmp[3],
            ]
        
    def _get_command_webm(self):
        cmd = [
            'ffmpeg', '-i', self._get_src_path(), '-r', '25', '-mbd', '1', '-vf', 'scale=trunc(oh*a/2)*2:480', 
            '-vcodec', 'libvpx', '-acodec', 'libvorbis', '-f', 'webm', '-g', '30', '-ar', '22050'
            ]
        cmd.extend(self.video_quality_params.get(get_entry_val(ConfigEntry.CONTENT_QUALITY_OF_CONTENT),
                   self.video_quality_params.get(ConfigEntry.QUALITY_TYPE_MEDIUM)))
        cmd.extend(['-y', self._tmp[0]])
        return cmd
    
    def _get_command_ogv(self):
        cmd = [
            'ffmpeg', '-i', self._get_src_path(), '-r', '25', '-mbd', '1', '-vf', 'scale=trunc(oh*a/2)*2:480', 
            '-vcodec', 'libtheora', '-acodec', 'libvorbis', '-g', '30', '-ar', '22050'
            ]
        cmd.extend(self.video_quality_params.get(get_entry_val(ConfigEntry.CONTENT_QUALITY_OF_CONTENT),
                   self.video_quality_params.get(ConfigEntry.QUALITY_TYPE_MEDIUM)))
        cmd.extend(['-y', self._tmp[1]])
        return cmd
    
    def _get_command_mp4(self):
        cmd = [
            'ffmpeg', '-i', self._get_src_path(), '-r', '25', '-mbd', '1', '-vf', 'scale=trunc(oh*a/2)*2:480', 
            '-vcodec', 'libx264', '-acodec', 'libfaac', '-g', '30', '-ar', '22050'
            ]  
        cmd.extend(self.video_quality_params.get(get_entry_val(ConfigEntry.CONTENT_QUALITY_OF_CONTENT),
                   self.video_quality_params.get(ConfigEntry.QUALITY_TYPE_MEDIUM)))
        cmd.extend(['-y', self._tmp[2]])
        return cmd

    def _get_command_flv(self):
        return {
            ConfigEntry.QUALITY_TYPE_HIGH: self._get_command_high_quality(),
            ConfigEntry.QUALITY_TYPE_MEDIUM: self._get_command_medium_quality(),
            ConfigEntry.QUALITY_TYPE_LOW: self._get_command_low_quality()
        }.get(get_entry_val(ConfigEntry.CONTENT_QUALITY_OF_CONTENT), self._get_command_medium_quality())

    def _convert(self):
        try:
            self._run_command(self._get_command_webm())
            self._run_command(self._get_command_ogv())
            self._run_command(self._get_command_mp4())
            self._run_command(self._get_command_flv())
        except utils.CommandError, e:
            self._logger.error(
                'Conversion of file.id=%d from %s has failed (retcode = %d). %s' % (
                    self._file.id, self._get_src_path(), e.code, e.stdout))
            raise ConversionError('Conversion of file.id=%d from %s has failed (retcode = %d)' % (
                    self._file.id, self._get_src_path(), e.code))
            
        self._run_command(self._get_thumbnail_command())
        self._run_command(self._get_preview_command())
        self._file.duration=self._get_length()

    def _get_thumbnail_command(self):
        return ['ffmpeg',  '-itsoffset', '-4', '-i', self._get_src_path(), '-vcodec', 'mjpeg',
                '-vframes', '1', '-an', '-f' , 'rawvideo', '-s',  '138x99', self._get_thumbnail_path()]

    def _get_preview_command(self):
        return ['ffmpeg',  '-itsoffset', '-4', '-i', self._get_src_path(), '-vcodec', 'mjpeg',
                '-vframes', '1', '-an', '-f' , 'rawvideo', '-s',  '856x480', self._get_preview_path()]

class AudioConverter(MediaConverter):
    
    def _initialize(self):
        self._tmp = list()
        for i in range(2):
            self._tmp.append(self._gen_tmp_path(''.join(['.',
                                ConfigEntry.CONTENT_AUDIO_FORMATS[i]])))
    
    def _get_mp3_command(self):
        return [
            'ffmpeg', '-i', self._get_src_path(), '-acodec', 'libmp3lame',
            '-ar', '22050', '-ab', '64000', '-f', 'mp3', '-y', self._tmp[0]
        ]

    def _get_ogg_command(self):
        return [
            'ffmpeg', '-i', self._get_src_path(), '-acodec', 'libvorbis',
            '-ar', '22050', '-ab', '64000', '-y', self._tmp[1]
        ]

    def _convert(self):
        try:
            self._run_command(self._get_mp3_command())
            self._run_command(self._get_ogg_command())
        except utils.CommandError, e:
            self._logger.error(
                'Conversion of file.id=%d from %s has failed (retcode = %d). %s' % (
                    self._file.id, self._get_src_path(), e.code, e.stdout))
            raise ConversionError('Conversion of file.id=%d from %s has failed (retcode = %d)' % (
                    self._file.id, self._get_src_path(), e.code))
        self._file.duration=self._get_length()

class HtmlConverter(BaseConverter):
    def _convert(self):
        try:
            self._run_command(self._get_thumbnail_command())
            self._run_command(self._get_preview_command())
        except Exception, e:
            print e

    def _get_thumbnail_command(self):
        return ['convert', '-scale', '138x99', self._get_src_path() + "[0]", 'jpeg:' + self._get_thumbnail_path()]

    def _get_preview_command(self):
        return ['convert', '-scale', '856x480', self._get_src_path() + "[0]", 'jpeg:' + self._get_preview_path()]
    
class TXTConverter(BaseConverterWithTempFile):
    def _convert(self):
        with open(self._get_src_path(), 'r') as src_file:
            file_content = src_file.readlines()

        with open(self._tmp, 'w') as dst_file:
            dst_file.write('<PRE>\n')
            for line in file_content:
                dst_file.write(line)
            dst_file.write('</PRE>\n')
        self._run_command(self._get_thumbnail_command())
        self._run_command(self._get_preview_command())

    def _get_thumbnail_command(self):
        return ['convert', '-scale', '138x99', self._get_src_path() + "[0]", 'jpeg:' + self._get_thumbnail_path()]

    def _get_preview_command(self):
        return ['convert', '-scale', '856x480', self._get_src_path() + "[0]", 'jpeg:' + self._get_preview_path()]

class ImageConverter(BaseConverterWithTempFile):
    def _get_command(self):
        cmd = [
            'convert', self._get_src_path(), 'png:' + self._tmp,
            ]

        return cmd

    def _convert(self):
        if self._file_convertable():
            super(ImageConverter, self)._convert()

        _, _, ext = self._file.orig_filename.rpartition('.')
        if ext.lower() == 'gif':
            src_path = self._get_src_path() + "[0]"
        else:
            src_path = self._get_src_path()
            
        self._run_command(self._get_thumbnail_command(src_path))
        self._run_command(self._get_preview_command(src_path))

    def _get_thumbnail_command(self, src_path):
        return ['convert', '-scale', '138x99', src_path, 'jpeg:' + self._get_thumbnail_path()]

    def _get_preview_command(self, src_path):
        return ['convert', '-scale', '856x480', src_path, 'jpeg:' + self._get_preview_path()]

class PDFConverter(BaseConverterWithTempDir):
    def _get_command(self):
        dst = os.path.join(self._tmp, 'p.png')
        return ['convert', '-density', '400', '-resize', '25%', '-quality', '92', self._get_src_path(), dst]

    def _run_command(self, cmd, cwd=None):
        output = super(PDFConverter, self)._run_command(cmd, cwd)
        if output and output.startswith('Error'):
            raise ConversionError(
                'Error during conversion of a PDF file (file id: %d): "%s" to images' % (
                    self._file.id, output.splitlines()[0]))
        for file_name in fnmatch.filter(os.listdir(self._tmp), '*.htm?'):
            if os.path.exists(os.path.join(self._tmp,file_name)):
                os.unlink(os.path.join(self._tmp,file_name))

        pages_num = len(fnmatch.filter(os.listdir(self._tmp), 'p*.png'))
        if pages_num > 1:
            for i in range(0,pages_num):
                file_name = 'p-%d.png'%i
                result_name = 'p-%d.html'%(i+1)
                with open(os.path.join(self._tmp, result_name), 'w') as html_file:
                    html_file.write('<HTML>\n')
                    html_file.write('<BODY>\n')
                    html_file.write('<IMG SRC="%s"></IMG>\n'%file_name)
                    html_file.write('</BODY>\n')
                    html_file.write('</HTML>\n')
        elif pages_num == 1:
            with open(os.path.join(self._tmp, 'p-1.html'), 'w') as html_file:
                    html_file.write('<HTML>\n')
                    html_file.write('<BODY>\n')
                    html_file.write('<IMG SRC="%s"></IMG>\n'%'p.png')
                    html_file.write('</BODY>\n')
                    html_file.write('</HTML>\n')
        self._file.pages_num = pages_num
        self._file.save()
        
    def _get_thumbnail_command(self):
        return ['convert', '-scale', '138x99', self._get_src_path() + "[0]", 'jpeg:' + self._get_thumbnail_path()]

    def _get_preview_command(self):
        return ['convert', '-scale', '856x480', self._get_src_path() + "[0]", 'jpeg:' + self._get_preview_path()]

    def _convert(self):
        super(PDFConverter, self)._convert()
        self._convert_thumbnail()
        self._convert_preview()

    def _convert_thumbnail(self):
        super(BaseConverterWithTempDir, self)._run_command(self._get_thumbnail_command())

    def _convert_preview(self):
        super(BaseConverterWithTempDir, self)._run_command(self._get_preview_command())

class OfficeConverter(PDFConverter):
    """
       Class for converting office format files.
        Office files are converted as follows:
            src_file -> pdf -> html

    """
    def _get_tmp_path(self):
        path = os.path.join(self._tmp, 'tmp.pdf')
        return self._storage.path(path)

    def _get_src_path(self):
        return self._get_tmp_path()

    def _get_command(self):
        cmd = ['unoconv', '-f', 'pdf', '-p', str(settings.OO_CONVERTER_PORT), super(OfficeConverter, self)._get_src_path()]
        return cmd

    def _run_command(self, cmd, cwd=None):
        super(BaseConverterWithTempDir, self)._run_command(cmd=cmd, cwd=cwd)

    def _convert(self):
        try:
            output = self._run_command(self._get_command())
            print output
            base, ext = os.path.splitext(super(OfficeConverter, self)._get_src_path())

            shutil.copy(base+'.pdf', self._get_tmp_path())
            output = super(OfficeConverter,self)._run_command(super(OfficeConverter,self)._get_command())
            print output
            self._run_command(self._get_thumbnail_command(base+'.pdf'))
            self._run_command(self._get_preview_command(base+'.pdf'))
        except Exception, error:
            self._logger.error(error)
            raise ConversionError(
                'Error converting file (file id: %d). %s' % (
                    self._file.id, error))
        finally:
            super(BaseConverterWithTempDir,self)._finalize()

    def _get_thumbnail_command(self, src):
        return ['convert', '-scale', '138x99', src + "[0]" , 'jpeg:' + self._get_thumbnail_path()]

    def _get_preview_command(self, src):
        return ['convert', '-scale', '856x480', src + "[0]" , 'jpeg:' + self._get_preview_path()]
    
def register(type, class_):
    """Registers new converter for the given file type.

    :param type: Id of the file type.
    :param class_: Class impementing converter.

    :return: Previous converter class or None.
    """

    old = unregister(type)
    _converters[type] = class_
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
register(models.File.TYPE_SCORM, ScormConverter)
register(models.File.TYPE_VIDEO, VideoConverter)
register(models.File.TYPE_AUDIO, AudioConverter)
register(models.File.TYPE_IMAGE, ImageConverter)
register(models.File.TYPE_PDF, PDFConverter)
register(models.File.TYPE_PLAIN, TXTConverter)
register(models.File.TYPE_MSPPT, OfficeConverter)
register(models.File.TYPE_MSDOC, OfficeConverter)
register(models.File.TYPE_HTML, HtmlConverter)


# vim: set et sw=4 ts=4 sts=4 tw=78:
