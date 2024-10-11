from datetime import datetime, timezone
from typing import Callable

from chat.messages import ColdMessage, Message, UserMessage

SYSTEM_HEADER = """\
Today's date is {datetime}

"""


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
            cold_message = message.freeze()
            self.recorder(cold_message)
            self.history.append(cold_message)

    def render_to_openai(self, system_message: str = None, request: str = None, system_header: str = None) -> list[
        dict]:
        if system_message is None:
            system_message = ""

        if system_header is None:
            system_header = SYSTEM_HEADER.format(datetime=datetime.now(tz=timezone.utc))

        return [m for m in self.__message_renderer(system_header + system_message, request)]

    def __message_renderer(self, system_message: str, request: str):
        yield {"role": "system", "content": system_message}

        for message in self.history:
            for role_and_content in message.read("role_and_content"):
                yield role_and_content

        if request is not None:
            atomized_request = UserMessage(f"First address the following request: {request}")
            for role_and_content in atomized_request.to_role_and_content():
                yield role_and_content
