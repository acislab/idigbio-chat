from chat.conversation import Conversation, UserMessage
from chat.tools.tool import all_tools
from nlp.agent import Agent

tool_lookup = {t.schema["name"]: t for t in all_tools}
function_definitions = [p.schema for p in all_tools]


def create_plan(agent: Agent, history: Conversation, request: str):
    tool_name = _pick_a_tool(agent, history, request)
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


def _pick_a_tool(agent: Agent, history: Conversation, request: str) -> str:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=None,
        max_tokens=100,
        functions=function_definitions,
        messages=history.render_to_openai(_PICK_A_TOOL_PROMPT, request)
    )

    fn_call = result.choices[0].message.function_call
    # if fn_call is None or fn_call.name in ("converse", "ask_an_expert"):
    if fn_call is None:
        return "converse"
    else:
        tool_name = fn_call.name
        return "converse" if tool_name is None else tool_name
