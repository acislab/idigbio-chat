import json

import fields
from chat.agent import Agent
from idigbio_records_api_schema import LLMQueryOutput

SYSTEM_PROMPT = """
You translate iDigBio Records Search API parameters into natural language requests. If a request is provided as 
input, try to adjust that request to fit the new parameters. 

## Example 1

reference request: Homo sapiens in North America
rq: {
    "genus": "Homo",
    "specificepithet", "sapiens",
    "continent": "Asia"
}

You: Homo sapiens in Asia

## Example 2 

reference request: records for Homo sapiens in North America and also South America
rq: {
    "scientificname": "Rattus rattus",
    "continent": "Asia,Europe"
}

You: records for Rattus rattus in Asia and also Europe
"""


def run(agent: Agent, data: dict) -> dict:
    reference_input = data["input"]
    rq = data["rq"]

    new_input = generate_new_input_from_rq(agent, reference_input, rq)

    # Make sure new input translates to the given rq

    return {
        "input": new_input,
        "rq": rq,
        "result": "success",
        "message": ""
    }


def generate_new_input_from_rq(agent, reference_input, rq) -> str:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        max_tokens=100,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }, {
                "role": "user",
                "content": json.dumps({"input": reference_input, "rq": rq})
            }
        ]
    )

    new_input = result.choices[0].message.content
    return new_input


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
