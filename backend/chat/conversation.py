from enum import Enum
from typing import Iterator, Iterable

import requests

import search
from chat.chat_util import stream_openai, stream_as_json
from chat.stream_util import StreamedContent, StreamedString
from nlp.agent import Agent
from schema.idigbio.api import IDigBioRecordsApiParameters, IDigBioSummaryApiParameters, IDigBioDownloadApiParameters


class MessageType(Enum):
    user_text_message = "user_text_message"
    ai_text_message = "ai_text_message"
    ai_map_message = "ai_map_message"
    ai_processing_message = "ai_processing_message"
    error = "error"


MessageValue = str | dict | list | StreamedContent


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
        pass

    def stream_type_and_value(self) -> Iterable[str]:
        return stream_as_json({"type": self.get_type().value, "value": self.value}) if self.show_user else []


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
    def __init__(self, summary: MessageValue, content: MessageValue, show_user: bool = True):
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
                "content": "".join(self.value["content"])
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


def generate_records_search_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioRecordsApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True)
    return params


def generate_records_summary_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioSummaryApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True)
    return params


def generate_records_download_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioDownloadApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True)
    return params


def get_record_count(query_url: str) -> (int, dict):
    res = requests.get(query_url)
    return res.json()["itemCount"], res.json()


def stream_record_counts_as_markdown_table(counts) -> str:
    top_field = [x for x in counts if x != "itemCount"][0]

    yield f"| {top_field} | count |\n"
    yield "|-|-|\n"
    for row in (f"| {k} | {v['itemCount']} |\n" for k, v in counts[top_field].items()):
        yield row
