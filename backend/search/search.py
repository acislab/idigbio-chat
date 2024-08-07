import json

import fields
from chat.agent import Agent
from idigbio_records_api_schema import LLMQueryOutput

SEARCH = {
    "name": "search_species_occurrence_records",
    "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                   "geographic distribution."
}

ABORT = {
    "name": "ask_an_expert",
    "description": "If none of the other tools satisfy the user's request, ask an expert for help."
}


def search(agent: Agent, user_input: str):
    should_parse = check_if_user_input_is_on_topic(agent, user_input)

    if should_parse:
        return search_species_occurrence_records(agent, user_input)
    else:
        return report_failure(agent, user_input)


def check_if_user_input_is_on_topic(agent, user_input):
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        max_tokens=100,
        functions=[SEARCH, ABORT],
        messages=[
            {
                "role": "system",
                "content": "You call functions to retrieve information that may help answer the user's "
                           "biodiversity-related queries. You do not answer queries yourself. If no other "
                           "functions match the user's query, call for help from an expert using the "
                           "ask_an_expert function."
            }, {
                "role": "user",
                "content": user_input
            }
        ]
    )

    procedure_name = result.choices[0].message.function_call.name
    return procedure_name == "search_species_occurrence_records"


SEARCH_PROMPT = f"""
You translate user requests into parameters for the iDigBio record search API. Here is 
a list of fields you may use:

{json.dumps(fields.fields)}

If the user specifies a binomial 
scientific name, try to break it up into its genus and specific epithet. However, if the user 
specifies that they want to search for an exact scientific name, use the "scientificname" field. If the user places 
something in quotes, use the full text that is quoted, do not break it up.

## Example 1

User: "Homo sapiens"
You: {{
    "genus": "Homo",
    "specificepithet: "sapiens
}}

## Example 2

User: "Only Homo sapiens Linnaeus, 1758"
You: {{
    "scientificname": "Homo sapiens Linnaeus, 1758"
}}

## Example 3

User: "Scientific name \"this is fake but use it anyway\""
You: {{
    "scientificname": "this is fake but use it anyway"
}}
"""


def search_species_occurrence_records(agent: Agent, user_input: str):
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=LLMQueryOutput,
        messages=[
            {
                "role": "system",
                "content": SEARCH_PROMPT
            }, {
                "role": "user",
                "content": user_input
            }
        ],
    )

    params = result.model_dump(exclude_none=True)

    return {
        "input": user_input,
        "rq": params["rq"],
        "result": "success",
        "message": ""
    }


def report_failure(agent: Agent, user_input: str):
    return {
        "input": user_input,
        "rq": {},
        "result": "error",
        "message": "Failed to understand user input"
    }
