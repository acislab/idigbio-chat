import json
from typing import Iterable


def escape(s: str):
    return json.dumps(s)[1:-1]


def stream_as_json(value):
    if isinstance(value, str):
        yield json.dumps(value)
    elif isinstance(value, dict):
        yield "{"
        for i, (k, v) in enumerate(value.items()):
            if i > 0:
                yield ","
            yield f'{json.dumps(k)}:'
            for fragment in stream_as_json(v):
                if fragment is not None:
                    yield fragment
        yield "}"
    elif isinstance(value, list):
        yield "["
        for i, v in enumerate(value):
            if i > 0:
                yield ","
            for fragment in stream_as_json(v):
                if fragment is not None:
                    yield fragment
        yield "]"
    elif isinstance(value, Iterable):
        yield '"'
        for fragment in value:
            if isinstance(fragment, str):
                yield escape(fragment)
            elif fragment is not None:
                for v in stream_as_json(fragment):
                    yield v
        yield '"'
    else:
        yield '"'
        yield str(value)
        yield '"'


def stream_openai(response):
    for chunk in response:
        yield chunk.choices[0].delta.content


JSON_INDENT = 4


def __unindent__(s: str):
    return s[JSON_INDENT:]


def __not_blank__(s: str):
    return len(s) > 0


def __peel_pretty_json__(js: str):
    return "\n".join(filter(__not_blank__, map(__unindent__, js.split("\n"))))


def make_pretty_json_string(data: dict, peel: bool = True):
    as_text = "".join(stream_as_json(data))
    as_dict = json.loads(as_text)
    s = json.dumps(as_dict, indent=JSON_INDENT, separators=(",", ": "))
    return __peel_pretty_json__(s) if peel else s
