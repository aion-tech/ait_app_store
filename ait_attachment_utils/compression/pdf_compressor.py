from typing import List

from .abstract_compressor import Compressor


class PdfCompressor(Compressor):
    _extensions: List[str] = ["pdf"]

    def compress(self, data):
        raise NotImplementedError
