from typing import List, Iterable

from langgraph.graph.message import Messages
from pydantic import BaseModel, Field

from chat.conversation import Conversation, UserMessage, ErrorMessage, Message, AiChatMessage
from chat.plan import create_plan
from chat.tools.tool import all_tools
from nlp.agent import Agent

tool_lookup = {t.schema["name"]: t for t in all_tools}


def are_you_a_robot() -> Iterable[Message]:
    response = [
        AiChatMessage(
            "Hi! Before you can chat with me, please confirm you are a real person by entering \"I am not a robot\" "
            "into the text box at the bottom of the screen.")
    ]

    for ai_message in response:
        yield ai_message


def greet(agent: Agent, history: Conversation, user_text_message: str) -> Iterable[Messages]:
    history.append(UserMessage(user_text_message))
    return _respond_conversationally(agent, history)


def chat(agent: Agent, history: Conversation, user_text_message: str) -> Iterable[Message]:
    history.append(UserMessage(user_text_message))

    response = _make_response(agent, history, user_text_message)

    for ai_message in response:
        yield ai_message
        history.append(ai_message)


def _handle_individual_request(agent, history, request) -> Iterable[Message]:
    plan = create_plan(agent, history, request)
    tool_name = plan

    if tool_name in tool_lookup:
        tool = tool_lookup[tool_name]()

        response = tool.call(
            agent=agent,
            request=request,
            history=history,
            state={}
        )

        for message in response:
            message.tool_name = tool_name
            yield message
    else:
        yield ErrorMessage(f"Tried to use undefined tool \"{tool_name}\"")


def _make_response(agent: Agent, history: Conversation, user_message: str) -> Iterable[Message]:
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
        for message in _respond_conversationally(agent, history):
            yield message
    else:
        for request in requests:
            for message in _handle_individual_request(agent, history, request):
                yield message


HELP_MESSAGE = """\
This is a prototype chatbot that intelligently uses the iDigBio portal to find and discover species
occurrence records and their media.

Here are some examples of questions this chatbot can answer:

* "How many records does iDigBio have for occurrences in Canada?"
* "Find records of *Acer saccharum* that have images in iDigBio"
* "Show a map of *Ursus arctos* occurrences"
* "What species has the most reported occurrences in Okinawa, Japan?"

If you'd like to provide feedback or want to know more about this service, you can reach the
developers at https://github.com/acislab/idigbio-chat/issues.

Type "help" to repeat this message.
"""


def _get_baked_response(agent, history, user_message) -> Iterable[Message]:
    match user_message.lower():
        case "help":
            yield AiChatMessage(HELP_MESSAGE)
        case _:
            pass


def _respond_conversationally(agent, history):
    tool = tool_lookup["converse"]()
    response = tool.call(
        agent=agent,
        history=history,
        state={}
    )

    for message in response:
        yield message


BREAK_DOWN_PROMPT = """
You identify what a user wants. If the user requests multiple things, you break them up into a list of individual 
requests. Each item in the list should fully describe each individual request, even if it is redundant with the other 
items in the list. If the user only wants one thing, represent it as a list with one item. Format lists as JSON 
arrays. If the user is not requesting any specific information, create an empty array. Only break down the user's 
last message. Do not repeat requests that have already been addressed, unless the user's latest message is a 
follow-up to an earlier request. For example, if the user provides additional information to refine an earlier request.

Here are some examples of breaking down user request.

EXAMPLE 1

- User: I want to know what plant species are present in Florida and how many records iDigBio has for each species
- Assistant: ["what plant species are present in Florida", "how many records does iDigBio have for each species present 
in Florida"] 

The user's last message was the following:

{0}
"""


class RequestBreakdown(BaseModel):
    """
    This schema represents a list of individual requests extracted from a user message.
    """
    requests: List[str] = Field(...,
                                description="This is an array of individual requests like \"show a map of Homo "
                                            "sapiens\" or "
                                            "\"count the number of records for Homo Sapiens in iDigBio\".")


def _break_down_message_into_smaller_requests(agent: Agent, history: Conversation, user_message: str) -> [str]:
    response = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        max_retries=5,
        response_model=RequestBreakdown,
        messages=history.render_to_openai(BREAK_DOWN_PROMPT.format(user_message)),
    )

    return response.requests
