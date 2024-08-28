import json
from typing import Iterable

PRESENT_RESULTS_PROMPT = """
You are an assistant who announces what information is about to be provided to the user. You do not provide the 
information itself. You not know anything. You do not answer questions directly. Start all of your responses with 
\"Here is\" and end them with a colon. For example, \"Here is {0}:\""

The user is about to be shown {0}.
"""


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
    elif isinstance(value, Iterable):
        for fragment in value:
            if isinstance(fragment, str):
                yield fragment
            elif fragment is not None:
                for v in stream_value_as_text(fragment):
                    yield v
    else:
        yield str(value)


def stream_openai(response):
    yield '"'
    for chunk in response:
        yield chunk.choices[0].delta.content
    yield '"'


def json_to_markdown(data: dict):
    as_text = "".join(stream_value_as_text(data))
    as_dict = json.loads(as_text)
    return ("```json\n" + json.dumps(as_dict, indent=4, separators=(",", ": ")) + "\n```\n").replace("\n", "\\n")
