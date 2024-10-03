import json
from enum import Enum
from typing import Any, Iterator
from typing import Iterable

from chat.content_streams import StreamedContent
from chat.utils.json import stream_as_json


class MessageType(Enum):
    user_text_message = "user_text_message"
    ai_text_message = "ai_text_message"
    ai_map_message = "ai_map_message"
    ai_processing_message = "ai_processing_message"
    error = "error"


MessageValue = str | dict | list | StreamedContent


class ColdMessage:
    __raw: dict[str, Any]

    def __init__(self, **kwargs):
        self.__raw = dict()

        for k, v in kwargs.items():
            self.__raw[k] = json.dumps(v)

    def read(self, key):
        return json.loads(self.__raw[key])

    def read_all(self):
        return {k: self.read(k) for k in self.__raw}


class Message:
    value: MessageValue
    tool_name: str
    show_user: bool = True

    def __init__(self, value: MessageValue, show_user: bool = True):
        self.value = value
        self.tool_name = ""
        self.show_user = show_user

    def get_type(self) -> MessageType:
        pass

    def to_role_and_content(self) -> list[dict]:
        """
        Render in OpenAI format.
        """
        pass

    def stream_type_and_value(self) -> Iterable[str]:
        """
        Stream to the frontend.
        """
        return stream_as_json({"type": self.get_type().value, "value": self.value})

    def to_type_and_value(self) -> dict:
        return json.loads("".join(self.stream_type_and_value()))

    def freeze(self) -> ColdMessage:
        """
        Encode as json for persistent storage.
        """
        return ColdMessage(
            type=self.get_type().value,
            tool_name=self.tool_name,
            show_user=self.show_user,
            role_and_content=self.to_role_and_content(),
            type_and_value=self.to_type_and_value(),
        )


class UserMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.user_text_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "user",
                "content": self.value
            }
        ]


class AiChatMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.ai_text_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": "".join(self.value)
            }
        ]


class AiMapMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.ai_map_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": "This is a map of species occurrences around the globe."
            }
        ]


class AiProcessingMessage(Message):
    def __init__(self, summary: MessageValue, content: MessageValue, thoughts: MessageValue = None,
                 show_user: bool = True):
        self.thoughts = content if thoughts is None else thoughts
        super().__init__({"summary": summary, "content": content}, show_user)

    def get_type(self) -> MessageType:
        return MessageType.ai_processing_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "function",
                "name": self.tool_name,
                "content": self.value["summary"]
            },
            {
                "role": "function",
                "name": self.tool_name,
                "content": "".join(self.thoughts)
            }
        ]


class ErrorMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.error

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "error",
                "content": self.value
            }
        ]


def stream_messages(message_stream: Iterator[Message]) -> Iterator[str]:
    streamed_previous_message = False
    yield "["
    for i, message in enumerate(message_stream):
        if streamed_previous_message:
            yield ","
        if message.show_user:
            for fragment in message.stream_type_and_value():
                yield fragment
            streamed_previous_message = True
    yield "]"
