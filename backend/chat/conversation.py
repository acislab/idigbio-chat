from typing import Callable

from chat.messages import ColdMessage, Message, UserMessage


class Conversation:
    history: list[ColdMessage]
    recorder: Callable[[ColdMessage], None]

    def __init__(self, history: list[ColdMessage] = None, recorder: Callable[[ColdMessage], None] = None):
        if history is None:
            history = []
        if recorder is None:
            recorder = lambda x: x

        self.history = history
        self.recorder = recorder

    def append(self, messages: Message | list[Message]):
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            self.history.append(message.freeze())

    def render_to_openai(self, system_message: str = None, request: str = None) -> list[dict]:
        return [m for m in self.__message_renderer(system_message, request)]

    def __message_renderer(self, system_message: str, request: str):
        if system_message is not None:
            yield {"role": "system", "content": system_message}

        for message in self.history:
            for role_and_content in message.read("role_and_content"):
                yield role_and_content

        if request is not None:
            atomized_request = UserMessage(f"First address the following request: {request}")
            for role_and_content in atomized_request.to_role_and_content():
                yield role_and_content
