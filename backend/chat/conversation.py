from datetime import datetime, timezone
from typing import Callable, Optional

from chat.messages import ColdMessage, Message, UserMessage

SYSTEM_HEADER = """\
Today's date is {datetime}

"""


class Conversation:
    history: list[ColdMessage]
    recorder: Callable[[ColdMessage, Optional[str]], None]
    conversation_id: str | None

    def __init__(self, history: list[ColdMessage] = None,
                 recorder: Callable[[ColdMessage, Optional[str]], None] = None, conversation_id: str = None):
        if history is None:
            history = []
        if recorder is None:
            recorder = lambda x, y: (x, y)

        self.history = history
        self.recorder = recorder
        self.conversation_id = conversation_id

    def append(self, messages: Message | list[Message]):
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            cold_message = message.freeze()
            self.recorder(cold_message, self.conversation_id)
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
            yield from message.read("role_and_content")

        if request is not None:
            atomized_request = UserMessage(f"First address the following request: {request}")
            yield from atomized_request.to_role_and_content()
