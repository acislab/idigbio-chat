from chat.conversation import Conversation, Message, MessageType
from nlp.agent import Agent


def chat(agent: Agent, history: list, user_message: str) -> dict:
    conversation = Conversation(history)
    conversation.append(Message(MessageType.user, user_message))

    response = Message(MessageType.system, "This is a test")

    conversation.append(response)

    return response.to_dict()
