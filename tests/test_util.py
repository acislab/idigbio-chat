from chat_test.messages import UserMessage, Message
from chat_test.conversation import Conversation


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
