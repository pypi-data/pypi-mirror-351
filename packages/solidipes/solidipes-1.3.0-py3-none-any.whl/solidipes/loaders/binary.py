import os

from datasize import DataSize

from ..validators.validator import add_validation_error, validator
from .file import File


class Binary(File):
    """File of unsupported type."""

    def __init__(self, **kwargs) -> None:
        from ..viewers.binary import Binary as BinaryViewer

        super().__init__(**kwargs)
        self.compatible_viewers[:0] = [BinaryViewer]

    @File.cached_property
    def text(self):
        text = ""
        if self.file_info.type:
            text += f"File type: {self.file_info.type}\n"

        text += f"File size: {DataSize(self.file_info.size):.2a}"
        return text

    @validator(description="File type supported", mandatory=False)
    def _has_valid_extension(self) -> bool:
        add_validation_error([
            f"Unknown extension '{os.path.splitext(self.file_info.path)[1]}' (detected filetype is"
            f" '{self.file_info.type}')"
        ])
        return False
