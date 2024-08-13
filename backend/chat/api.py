from chat.conversation import Conversation, UserMessage
from chat.plan import create_plan
from nlp.agent import Agent
from chat.tools.tool import all_tools

tool_lookup = {t.schema["name"]: t for t in all_tools}


def chat(agent: Agent, history: list, user_message: str) -> dict:
    conversation = Conversation(history)
    conversation.append(UserMessage(user_message))

    plan = create_plan(agent, conversation, user_message)

    response = tool_lookup[plan]().call(
        agent=agent,
        request=user_message,
        conversation=conversation,
        state={}
    )

    conversation.append(response)

    return response.to_dict()
