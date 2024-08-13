from chat.conversation import Conversation, Message, MessageType, UserMessage, AiMessage
from chat.plan import create_plan
from nlp.agent import Agent
from tools.tool import all_tools

tool_lookup = {t.schema["name"]: t for t in all_tools}


def chat(agent: Agent, history: list, user_message: str) -> dict:
    conversation = Conversation(history)
    conversation.append(UserMessage(user_message))

    plan = create_plan(agent, conversation, user_message)

    response = tool_lookup[plan]().call(agent, conversation)

    conversation.append(response)

    return response.to_dict()
