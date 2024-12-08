import json
from enum import Enum
from typing import Any, Iterator
from uuid import uuid4

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

    def __init__(self, raw: dict = None, **kwargs):
        if raw is None:
            self.__raw = dict()
        else:
            self.__raw = raw.copy()

        for k, v in kwargs.items():
            self.__raw[k] = v

    def read(self, key) -> Any:
        return self.__raw[key]

    def read_all(self) -> dict[str, Any]:
        return {k: self.read(k) for k in self.__raw}


class Message:
    message_id: str
    value: MessageValue
    tool_name: str

    def __init__(self, value: MessageValue):
        self.message_id = str(uuid4())
        self.value = value
        self.tool_name = ""

    def get_type(self) -> MessageType:
        pass

    def to_openai(self) -> list[dict]:
        """
        Render in OpenAI format.
        """
        pass

    def stream_to_frontend(self) -> Iterator[str]:
        """
        Stream to the frontend.
        """
        return stream_as_json({
            "id": self.message_id,
            "type": self.get_type().value,
            "value": self.value
        })

    def to_frontend(self) -> dict:
        return json.loads("".join(self.stream_to_frontend()))

    def freeze(self) -> ColdMessage:
        """
        Encode as json for persistent storage.
        """
        return ColdMessage(
            message_id=self.message_id,
            type=self.get_type().value,
            tool_name=self.tool_name,
            openai_messages=self.to_openai(),
            frontend_messages=self.to_frontend(),
        )


class UserMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.user_text_message

    def to_openai(self) -> list[dict]:
        return [
            {
                "role": "user",
                "content": self.value
            }
        ]


class AiChatMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.ai_text_message

    def to_openai(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": "".join(self.value)
            }
        ]


class AiMapMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.ai_map_message

    def to_openai(self) -> list[dict]:
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
        self.show_user = show_user
        super().__init__({"summary": summary, "content": content})

    def get_type(self) -> MessageType:
        return MessageType.ai_processing_message

    def to_openai(self) -> list[dict]:
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

    def stream_to_frontend(self) -> Iterator[str]:
        if self.show_user:
            yield from super().stream_to_frontend()
        else:
            yield "[]"


class ErrorMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.error

    def to_openai(self) -> list[dict]:
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
        yield from message.stream_to_frontend()
        streamed_previous_message = True
    yield "]"
