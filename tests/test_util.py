from typing import Sized

from chat.messages import UserMessage, Message
from chat.conversation import Conversation


def repeat(n):
    print()  # pytest stdout doesn't end on a new line
    for i in range(0, n):
        print(f"  Attempt {i}")
        yield n


def test_conversation(m: str | Message | list[Message]):
    conv = Conversation()

    if isinstance(m, str):
        m = UserMessage(m)

    if isinstance(m, Message):
        m = [m]

    for m in m:
        conv.append(m)

    return conv


def clean(data: dict):
    if not isinstance(data, dict):
        return data
    else:
        return {k: clean(v) for k, v in data.items() if not is_empty(v)}


def is_empty(data):
    return len(data) == 0 if isinstance(data, Sized) else False
