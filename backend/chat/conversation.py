import json
from enum import Enum
from typing import Callable, Any
from typing import Iterator, Iterable

from chat.chat_util import stream_openai, stream_as_json
from chat.stream_util import StreamedContent, StreamedString
from nlp.agent import Agent


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
        return stream_as_json({"type": self.get_type().value, "value": self.value}) if self.show_user else ""

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


PRESENT_RESULTS_PROMPT = """
You are an assistant who relays information to the user. You not know anything. Only use what information has been 
provided to you as context to address the user's request. If some context information indirectly answers the user's 
question, try to cite that information. For example, if the user wants to know whether a species is present in a 
particular location, and if the context information shows that there are 1000 records of the species in that location, 
then mention the number of records instead of just saying "Yes". So, a good response might be "Yes, there are 1000 
records of the species in that location"

If the provided context information does help you answer to the user's request, apologize that you could not 
answer their request. Do not respond with any information that is not already available in the conversation or 
provided context.

Use the context information below:

{context}
"""


def present_results(agent: Agent, history: Conversation, request: str, results: str | StreamedString):
    response = agent.openai.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=history.render_to_openai(PRESENT_RESULTS_PROMPT.format(request=request, context=results), request),
        stream=True,
    )

    return AiChatMessage(stream_openai(response))


def stream_response_as_text(message_stream: Iterator[Message]) -> Iterator[str]:
    nonempty = False
    yield "["
    for i, message in enumerate(message_stream):
        if nonempty:
            yield ","
        for fragment in message.stream_type_and_value():
            yield fragment
            nonempty = True
    yield "]"
