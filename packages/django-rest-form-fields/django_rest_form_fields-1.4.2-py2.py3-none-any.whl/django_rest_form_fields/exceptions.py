"""
This file contains exceptions, raised by forms.* modules
"""
from typing import List

from django.core.exceptions import ValidationError


class FileSizeError(ValidationError):
    def __init__(self, allowed_size, file_size):  # type: (int, int) -> None
        error = "File is too big, max %d bytes are allowed (it has %d bytes)." % (allowed_size, file_size)
        super(FileSizeError, self).__init__(error, code=413)


class FileTypeError(ValidationError):
    def __init__(self, extension, valid_extensions):  # type: (str, List[str]) -> None
        error = "File has invalid type, only [%s] are allowed (it has '%s')."  \
                % (', '.join(valid_extensions), extension)
        super(FileTypeError, self).__init__(error, code=422)
