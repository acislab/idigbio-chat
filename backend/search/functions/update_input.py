import json

import fields
from chat.agent import Agent
from idigbio_records_api_schema import LLMQueryOutput

SYSTEM_PROMPT = """
You translate iDigBio Records Search API parameters into natural language requests. If a request is provided as 
input, try to adjust that request to fit the new parameters, changing as little as possible. If the request follows a 
particular format, reuse that format.

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

## Example 3

reference request: species = Homo sapiens, continent = North America
rq: {
    "genus": "Homo",
    "specificepithet", "sapiens",
    "continent": "Asia"
}

You: species = Homo sapiens, continent = Asia
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
