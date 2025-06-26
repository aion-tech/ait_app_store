from typing import List

from .abstract_compressor import Compressor


class HeicCompressor(Compressor):
    _extensions: List[str] = ["heic"]

    def compress(self, data):
        raise NotImplementedError
