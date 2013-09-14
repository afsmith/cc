from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.conf import settings


class MaxFileMemoryFileUploadHandler(MemoryFileUploadHandler):
    def handle_raw_input(self, input_data, META, content_length,
                         boundary, encoding=None):
        if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            self.activated = False
        else:
            self.activated = True


class MaxFileTemporaryFileUploadHandler(TemporaryFileUploadHandler):

    def handle_raw_input(self, input_data, META, content_length,
                         boundary, encoding=None):
        if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            self.activated = False
        else:
            self.activated = True

    def new_file(self, file_name, *args, **kwargs):
        if self.activated:
            super(MaxFileTemporaryFileUploadHandler, self).new_file(file_name,
                                                                    *args,
                                                                    **kwargs)

    def receive_data_chunk(self, raw_data, start):
        if self.activated:
            super(MaxFileTemporaryFileUploadHandler, self).receive_data_chunk(
                raw_data, start
            )

    def file_complete(self, file_size):
        if self.activated:
            super(MaxFileTemporaryFileUploadHandler, self).file_complete(file_size)
        else:
            return None
