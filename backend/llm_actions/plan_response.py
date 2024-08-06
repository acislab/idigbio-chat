import instructor
import openai
from dotenv import load_dotenv

import idigbio_util
from llm_actions.expert_opinion import ask_llm_for_expert_opinion
from llm_actions.search_idigbio import ask_llm_to_generate_search_query

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI())


class Functions:
    search_species_occurrence_records = {
        "name": "search_species_occurrence_records",
        "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                       "geographic distribution."
    }
    ask_an_expert = {
        "name": "ask_an_expert",
        "description": "If none of the other tools satisfy the user's request, ask an expert for help."
    }


ALL_FUNCTIONS = [
    Functions.search_species_occurrence_records,
    Functions.ask_an_expert
]


def ask_llm_to_call_a_function(prompt, functions=ALL_FUNCTIONS):
    result = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        max_tokens=100,
        messages=[
            {
                "role": "system",
                "content": "You call functions to find species occurrence records that may help answer users' "
                           "biodiversity-related queries. You do not answer queries yourself. If no other functions "
                           "match the user's query, call for help from an expert using the ask_an_expert function."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        functions=functions
    )

    action = result.choices[0].message.function_call.name
    match action:
        case "search_species_occurrence_records":
            return ask_llm_to_generate_search_query(prompt)
        case _:
            return ask_llm_for_expert_opinion(prompt)
