from typing import List

from abc import ABC, abstractmethod


class Compressor(ABC):
    _extensions: List[str] = []

    def __init__(self, file: bytes):
        self.file = file

    @abstractmethod
    def compress(self, data):
        raise NotImplementedError
