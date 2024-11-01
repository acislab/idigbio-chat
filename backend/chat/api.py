from typing import List, Iterator

from pydantic import BaseModel, Field

from chat.conversation import Conversation
from chat.messages import UserMessage, ErrorMessage, Message, AiChatMessage
from chat.tools.tool import all_tools
from nlp.ai import AI

tool_lookup = {t.name: t for t in all_tools}


def are_you_a_robot() -> Iterator[Message]:
    response = [
        AiChatMessage(
            "Hi! Before we chat, please confirm you are a real person by telling me \"I am not a robot\".")
    ]

    for ai_message in response:
        yield ai_message


def greet(ai: AI, history: Conversation, user_text_message: str) -> Iterator[Message]:
    history.append(UserMessage(user_text_message))
    return _respond_conversationally(ai, history)


def chat(ai: AI, history: Conversation, user_text_message: str) -> Iterator[Message]:
    history.append(UserMessage(user_text_message))

    response = _make_response(ai, history, user_text_message)

    for ai_message in response:
        yield ai_message
        history.append(ai_message)


def _handle_individual_request(ai, history, request) -> Iterator[Message]:
    plan = create_plan(ai, history, request)
    tool_name = plan

    if tool_name in tool_lookup:
        tool = tool_lookup[tool_name]()

        response = tool.call(
            ai=ai,
            request=request,
            history=history,
            state={}
        )

        for message in response:
            message.tool_name = tool_name
            yield message
    else:
        yield ErrorMessage(f"Tried to use undefined tool \"{tool_name}\"")


def _make_response(ai: AI, history: Conversation, user_message: str) -> Iterator[Message]:
    baked_response = _get_baked_response(user_message)
    if baked_response is not None:
        i = 0
        for message in baked_response:
            i += 1
            yield message
        if i > 0:
            return

    requests = _break_down_message_into_smaller_requests(ai, history, user_message)

    if len(requests) == 0:
        for message in _respond_conversationally(ai, history):
            yield message
    else:
        for request in requests:
            for message in _handle_individual_request(ai, history, request):
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


def _get_baked_response(user_message) -> Iterator[Message]:
    match user_message.lower():
        case "help":
            yield AiChatMessage(HELP_MESSAGE)
        case "ping":
            yield AiChatMessage("pong")
        case _:
            pass


def _respond_conversationally(ai, history) -> Iterator[Message]:
    tool = tool_lookup["converse"]()
    response = tool.call(
        ai=ai,
        history=history,
        state={}
    )

    for message in response:
        yield message


BREAK_DOWN_PROMPT = """\
You identify what a user wants. If the user requests multiple things of different types, you break them up into a
list of individual requests. Each item in the list should fully describe each individual request, even if it is
redundant with the other items in the list. If the user only wants one thing, represent it as a list with one item.
Do not break up requests simply because they are long or very specific or have a lot of parameters or constraints. 
Format lists as JSON arrays. If the user is not requesting any specific information, create an empty array. Only 
break down the user's last message. If the user's last message is a follow up to earlier messages, factor those in as 
well.

Do not break up search requests unless the user specifically asks you to.

Here are some examples of breaking down user request.

EXAMPLE 1

- User: I want to know what plant species are present in Florida and to see them on a map
- Assistant: ["what plant species are present in Florida", "show plant species in Florida on a map"] 

EXAMPLE 2:

- User: Find records of A and B in countries X, Y, Z since 1994
- Assistant: ["Find records of A and B in countries X, Y, Z since 1994"]\
"""


class RequestBreakdown(BaseModel):
    """
    This schema represents a list of individual requests extracted from a user message.
    """
    requests: List[str] = Field(...,
                                description="This is an array of individual requests like \"show a map of Homo "
                                            "sapiens\" or "
                                            "\"count the number of records for Homo Sapiens in iDigBio\".")


def _break_down_message_into_smaller_requests(ai: AI, history: Conversation, user_message: str) -> [str]:
    response = ai.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        max_retries=5,
        response_model=RequestBreakdown,
        messages=history.render_to_openai(BREAK_DOWN_PROMPT.format()),
    )

    return response.requests


function_definitions = [{"name": t.name, "description": t.description} for t in all_tools]


def create_plan(ai: AI, history: Conversation, request: str) -> str:
    tool_name = _pick_a_tool(ai, history, request)
    return tool_name


_PICK_A_TOOL_PROMPT = """
You call functions to retrieve information that may help answer the user's biodiversity-related queries. You do not 
answer queries yourself. If the user is not requesting information or if no function addresses the user's query, 
call the function named "converse".

# Example 1

User: Hi!
You: converse

# Example 2

User: Please find records of Homo sapiens occurrences 
You: search_species_occurrence_records

# Example 3

User: What do porcupines eat?
You: ask_an_expert

# Example 4

User: Who are you and what do you do?
You: converse
"""


def _pick_a_tool(ai: AI, history: Conversation, request: str) -> str:
    result = ai.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=None,
        max_tokens=100,
        functions=function_definitions,
        messages=history.render_to_openai(_PICK_A_TOOL_PROMPT, request)
    )

    fn_call = result.choices[0].message.function_call
    if fn_call is None:
        return "converse"
    else:
        tool_name = fn_call.name
        return "converse" if tool_name is None else tool_name
