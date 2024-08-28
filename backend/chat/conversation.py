import typing
from collections.abc import Callable
from enum import Enum
from typing import Iterator

from chat.chat_util import PRESENT_RESULTS_PROMPT, stream_openai, stream_value_as_text, json_to_markdown
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

    def get_value(self) -> MessageValue:
        return self.value

    def to_role_and_content(self) -> list[dict]:
        pass


class UserMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.user_text_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "user",
                "content": self.get_value()
            }
        ]


class AiChatMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.ai_text_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": self.get_value()
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
    def __init__(self, summary: MessageValue, content: MessageValue):
        super().__init__({"summary": summary, "content": content})

    def get_type(self) -> MessageType:
        return MessageType.ai_processing_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": self.get_value()["summary"] + "\n\n" + "".join(
                    stream_value_as_text(self.get_value()["content"]))
            }
        ]


class ErrorMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.error

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "error",
                "content": self.get_value()
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


def present_results(agent, history, type_of_results):
    response = agent.openai.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=history.render_to_openai(PRESENT_RESULTS_PROMPT.format(type_of_results)),
        stream=True,
    )

    return AiChatMessage(stream_openai(response))


def stream_response_as_text(message_stream: Iterator[Message]) -> Iterator[str]:
    yield "["
    for i, message in enumerate(message_stream):
        if i > 0:
            yield ","
        for fragment in stream_value_as_text({"type": message.get_type().value, "value": message.get_value()}):
            yield fragment
    yield "]"
