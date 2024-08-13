from chat.conversation import Conversation, UserMessage, ErrorMessage
from chat.plan import create_plan
from chat.tools.tool import all_tools
from nlp.agent import Agent

tool_lookup = {t.schema["name"]: t for t in all_tools}


def chat(agent: Agent, history: Conversation, user_message: str):
    history.append(UserMessage(user_message))

    plan = create_plan(agent, history)
    tool_name = plan

    if tool_name in tool_name:
        response = tool_lookup[tool_name]().call(
            agent=agent,
            request=user_message,
            conversation=history,
            state={}
        )
    else:
        response = [ErrorMessage(f"Tried to use undefined tool \"{tool_name}\"")]

    history.append(response)

    return response
