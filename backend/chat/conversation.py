from enum import Enum


class MessageType(Enum):
    user_message = "user_message"
    ai_message = "ai_message"
    error = "error"


MessageValue = str | dict | list


class Message:
    value: MessageValue

    def __init__(self, value: MessageValue):
        self.value = value

    def get_type(self) -> MessageType:
        pass

    def to_dict(self) -> dict:
        return {
            "type": self.get_type().value,
            "value": self.value
        }

    def to_role_and_content(self) -> list[dict]:
        pass


class UserMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.user_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "user",
                "content": self.value
            }
        ]


class AiMessage(Message):
    def get_type(self) -> MessageType:
        return MessageType.ai_message

    def to_role_and_content(self) -> list[dict]:
        return [
            {
                "role": "assistant",
                "content": self.value
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
            case MessageType.ai_message:
                return AiMessage(d["value"])
            case MessageType.user_message:
                return UserMessage(d["value"])
            case MessageType.error:
                return ErrorMessage(d["value"])
            case _:
                raise Exception(f"Undefined message type \"{d['type']}\"")
    except Exception as e:
        return ErrorMessage(f"Failed to parse message data: {d}\n{e}")


class Conversation:
    def __init__(self, history):
        self.history: list[Message] = [_parse_message_from_dict(m) for m in history]

    def append(self, message: Message):
        self.history.append(message)

    def render_to_openai(self, system_message) -> list[dict]:
        return [m for m in self.__message_renderer(system_message)]

    def __message_renderer(self, system_message):
        yield {"role": "system", "content": system_message}
        for message in self.history:
            for role_and_content in message.to_role_and_content():
                yield role_and_content