# This import statement initializes all defined actions
# noinspection PyUnresolvedReferences
from chat.agent import Agent

from chat.conversation import Conversation
from tools.tool import all_tools

procedure_lookup = {t.schema["name"]: t for t in all_tools}
functions = [p.schema for p in all_tools]


def ask_llm_to_call_a_function(agent: Agent, conversation: Conversation):
    result = agent.client.user.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        max_tokens=100,
        functions=functions,
        messages=conversation.render("You call functions to retrieve information that may help answer the user's "
                                     "biodiversity-related queries. You do not answer queries yourself. If no other "
                                     "functions match the user's query, call for help from an expert using the "
                                     "ask_an_expert function.")
    )

    procedure_name = result.choices[0].message.function_call.name
    if procedure_name is None: procedure_name = "ask_an_expert"

    if procedure_name in procedure_lookup:
        return procedure_lookup[procedure_name].call(agent, conversation)
    else:
        return {
            "type": "error",
            "data": {
                "message": f"Tried to use undefined procedure \"{procedure_name}\""
            }
        }
