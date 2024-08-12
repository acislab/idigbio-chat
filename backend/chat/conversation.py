from enum import Enum


class MessageType(Enum):
    user = "user"
    system = "system"
    error = "error"


MessageContent = str | dict | list


class Message:
    type: MessageType
    content: MessageContent

    def __init__(self, type: MessageType, value: MessageContent):
        self.type = type
        self.content = value

    def to_dict(self):
        return {
            "type": self.type,
            "content": self.content
        }


def _parse_message_from_dict(d: dict):
    try:
        return Message(**d)
    except Exception as e:
        return Message(MessageType.error, f"Malformed data: {d}\n{e}")


class Conversation:
    def __init__(self, history):
        self.history: list[Message] = [_parse_message_from_dict(m) for m in history]

    def append(self, message: Message):
        self.history.append(message)
