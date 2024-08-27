from collections.abc import Iterator

from chat.conversation import Conversation, UserMessage, ErrorMessage, Message, AiChatMessage
from chat.plan import create_plan
from chat.tools.tool import all_tools
from nlp.agent import Agent

tool_lookup = {t.schema["name"]: t for t in all_tools}


def chat(agent: Agent, history: Conversation, user_text_message: str) -> Iterator[Message]:
    history.append(UserMessage(user_text_message))

    response = _make_response(agent, history, user_text_message)

    for r in response:
        history.append(UserMessage(user_text_message))
        yield r


def _make_response(agent: Agent, history: Conversation, user_message: str) -> Iterator[Message]:
    baked_response = _get_baked_response(agent, history, user_message)
    if baked_response is not None:
        i = 0
        for message in baked_response:
            i += 1
            yield message
        if i > 0:
            return

    requests = _break_down_message_into_smaller_requests(agent, history, user_message)

    if len(requests) == 0:
        pass
        # TODO: Respond directly
    else:
        for request in requests:
            plan = create_plan(agent, history, user_message)
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


def _get_baked_response(agent, history, user_message) -> Iterator[Message]:
    match user_message.lower():
        case "help":
            yield AiChatMessage("I have access to the following tools...")
        case _:
            pass


BREAK_DOWN_PROMPT = """
You identify what a user wants. If the user requests multiple things, you break them up into a list of individual 
requests. Each item in the list should fully describe each individual request, even if it is redundant with the other 
items in the list. If the user only wants one thing, represent it as a list with one item. Format lists as JSON 
arrays. If the user is not requesting any specific information, create an empty array.

Here's an example of breaking down a user's request.

User: I want to know what plant species are present in Florida and how many records iDigBio has for each species
Assistant: ["what plant species are present in Florida", "how many records does iDigBio have for each species present 
in Florida"]
"""


def _break_down_message_into_smaller_requests(agent: Agent, history: Conversation, user_message: str) -> [str]:
    return [user_message]
