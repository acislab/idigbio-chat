from typing import Iterator

from chat.conversation import AiChatMessage, Message

PRESENT_RESULTS_PROMPT = """
You are an assistant who announces what information is about to be provided to the user. You do not provide the 
information itself. You not know anything. You do not answer questions directly. Start all of your responses with 
\"Here is\" and end them with a colon. For example, \"Here is {0}:\""

The user is about to be shown {0}.
"""


def stream_response_as_text(message_stream: Iterator[Message]) -> Iterator[str]:
    yield "["
    for i, message in enumerate(message_stream):
        if i > 0:
            yield ","
        for fragment in stream_value_as_text({"type": message.get_type().value, "value": message.value}):
            yield fragment
    yield "]"


def quote(s):
    return '"' + s.replace('"', r'\"') + '"'


def stream_value_as_text(value):
    if isinstance(value, str):
        yield quote(value)
    elif isinstance(value, dict):
        yield "{"
        for i, (k, v) in enumerate(value.items()):
            if i > 0:
                yield ","
            yield f'{quote(k)}:'
            for fragment in stream_value_as_text(v):
                if fragment is not None:
                    yield fragment
        yield "}"
    else:
        for fragment in value:
            if isinstance(fragment, str):
                yield fragment
            elif fragment is not None:
                for v in stream_value_as_text(fragment):
                    yield v


def stream_openai(response):
    yield '"'
    for chunk in response:
        yield chunk.choices[0].delta.content
    yield '"'


def present_results(agent, history, type_of_results):
    response = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=history.render_to_openai(PRESENT_RESULTS_PROMPT.format(type_of_results)),
        stream=True,
    )

    return AiChatMessage(stream_openai(response))
