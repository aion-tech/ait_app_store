import mimetypes
import os
from typing import List, Type

from .abstract_compressor import Compressor
from .heic_compressor import HeicCompressor
from .pdf_compressor import PdfCompressor

COMPRESSORS: List[Type[Compressor]] = [
    HeicCompressor,
    PdfCompressor,
]


def get_extension(file_name: str) -> str:
    root, extension = os.path.splitext(file_name)
    return extension


def init_compressor(file: bytes, filename: str, mimetype: str):
    for compressor in COMPRESSORS:
        filename_ext = get_extension(filename)
        mimetype_ext = mimetypes.guess_extension(mimetype)

        compressor._extensions
        if (
            mimetype_ext in compressor._extensions
            or filename_ext in compressor._extensions
        ):
            return compressor(file)

    return None
