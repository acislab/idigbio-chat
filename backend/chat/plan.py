# This import statement initializes all defined actions
# noinspection PyUnresolvedReferences
from nlp.agent import Agent

from chat.conversation import Conversation
from chat.tools.tool import all_tools

tool_lookup = {t.schema["name"]: t for t in all_tools}
function_definitions = [p.schema for p in all_tools]


def create_plan(agent: Agent, conversation: Conversation):
    tool_name = pick_a_tool(agent, conversation)
    return tool_name


PICK_A_TOOL_PROMPT = """
You call functions to retrieve information that may help answer the user's biodiversity-related queries. You do not 
answer queries yourself. If no other functions match the user's query, call for help from an expert using the 
ask_an_expert function.
"""


def pick_a_tool(agent: Agent, conversation: Conversation) -> str:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=None,
        max_tokens=100,
        functions=function_definitions,
        tool_choice="required",
        messages=conversation.render_to_openai(PICK_A_TOOL_PROMPT)
    )

    tool_name = result.choices[0].message.function_call.name
    return "ask_an_expert" if tool_name is None else tool_name
