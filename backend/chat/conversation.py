import typing
from collections.abc import Callable
from enum import Enum

from chat.stream_util import StreamedContent


class MessageType(Enum):
    user_text_message = "user_text_message"
    ai_text_message = "ai_text_message"
    ai_map_message = "ai_map_message"
    ai_processing_message = "ai_processing_message"
    error = "error"


MessageValue = str | dict | list | StreamedContent


class Message:
    value: MessageValue

    def __init__(self, value: MessageValue):
        self.value = value

    def get_type(self) -> MessageType:
        pass

    def to_role_and_content(self) -> list[dict]:
        pass


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
                "content": self.value
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
    content_formatter: Callable[[typing.Any], str]

    def __init__(self, summary: MessageValue, content: MessageValue, content_formatter=None):
        super().__init__({"summary": summary, "content": content})
        self.content_formatter = content_formatter

    def get_type(self) -> MessageType:
        return MessageType.ai_processing_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": self.value
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


def _parse_message_from_dict(d: dict) -> Message:
    try:
        match MessageType(d["type"]):
            case MessageType.ai_text_message:
                return AiChatMessage(d["value"])
            case MessageType.user_text_message:
                return UserMessage(d["value"])
            case MessageType.error:
                return ErrorMessage(d["value"])
            case _:
                raise Exception(f"Undefined message type \"{d['type']}\"")
    except Exception as e:
        return ErrorMessage(f"Failed to parse message data: {d}\n{e}")


class Conversation:
    def __init__(self, history: list[dict] = None):
        if history is None:
            history = []

        self.history: list[Message] = [_parse_message_from_dict(m) for m in history]

    def append(self, message: Message | list[Message]):
        if isinstance(message, list):
            self.history.extend(message)
        else:
            self.history.append(message)

    def render_to_openai(self, system_message: str = None, request: str = None) -> list[dict]:
        return [m for m in self.__message_renderer(system_message, request)]

    def __message_renderer(self, system_message: str, request: str):
        if system_message is not None:
            yield {"role": "system", "content": system_message}

        for message in self.history:
            for role_and_content in message.to_role_and_content():
                yield role_and_content

        if request is not None:
            for role_and_content in UserMessage(
                    f"First address the following request: {request}").to_role_and_content():
                yield role_and_content
