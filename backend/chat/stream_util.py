import itertools
from typing import Iterator, Iterable, Callable

Content = str | dict


class StreamedContent():
    __content: Content
    __stream: Iterator[Content]
    __reducer: Callable[[Content, Content], Content]

    def __init__(self, stream: Iterable[Content], reducer):
        self.__content = ""
        self.__stream = self.__gobble(stream)
        self.__reducer = reducer

    def __iter__(self) -> Iterator[Content]:
        return itertools.chain(iter([self.__content]), self.__stream)

    def __gobble(self, stream) -> Iterator[Content]:
        for delta in stream:
            self.__content = self.__reducer(self.__content, delta)
            yield delta

    def get(self) -> Content:
        for _ in self.__stream:
            pass
        return self.__content


def _add_strings(a: str, b: str) -> str:
    return a + b


class StreamedString(StreamedContent):
    def __init__(self, stream: Iterable[Content]):
        super().__init__(stream, _add_strings)


def _take_last(a, b):
    return b


class StreamedLast(StreamedContent):
    def __init__(self, stream: Iterable[Content]):
        super().__init__(stream, _take_last)

    def __iter__(self) -> Iterator[Content]:
        return iter([self.get()])