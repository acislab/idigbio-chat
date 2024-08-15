import itertools
from typing import Iterator, Iterable


class StreamedString:
    __string: str
    __stream: Iterator[str]

    def __init__(self, stream: Iterable[str]):
        self.__string = ""
        self.__stream = self.__gobble(stream)

    def __iter__(self) -> Iterator[str]:
        return itertools.chain(iter([self.__string]), self.__stream)

    def __gobble(self, stream) -> Iterator[str]:
        for x in stream:
            self.__string += x
            yield x

    def get_string(self) -> str:
        for _ in self:
            pass
        return self.__string
