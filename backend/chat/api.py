from collections.abc import Iterator

from openai import OpenAI

from chat.conversation import Conversation, UserMessage, ErrorMessage, Message
from chat.plan import create_plan
from chat.tools.tool import all_tools
from nlp.agent import Agent

tool_lookup = {t.schema["name"]: t for t in all_tools}


def chat(agent: Agent, history: Conversation, user_message: str) -> Iterator[Message]:
    history.append(UserMessage(user_message))

    response = execute(agent, history, user_message)

    for r in response:
        history.append(UserMessage(user_message))
        yield r


def execute(agent: Agent, history: Conversation, user_message: str) -> Iterator[Message]:
    plan = create_plan(agent, history)
    tool_name = plan

    if tool_name in tool_lookup:
        tool = tool_lookup[tool_name]()

        response = tool.call(
            agent=agent,
            request=user_message,
            history=history,
            state={}
        )

        for message in response:
            yield message
    else:
        yield ErrorMessage(f"Tried to use undefined tool \"{tool_name}\"")
