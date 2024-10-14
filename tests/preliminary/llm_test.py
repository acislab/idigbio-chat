import instructor
import openai
import pytest
from dotenv import load_dotenv

from tests.test_util import repeat

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI())

SAMPLE_SIZE = 1


class Functions:
    search_species_occurrence_records = {
        "name": "search_species_occurrence_records",
        "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                       "geographic distribution."
    }
    retrieve_species_occurrence_records = {
        "name": "retrieve_species_occurrence_records",
        "description": "Retrieves a list of species occurrence records in JSON format. These records describe the "
                       "location and date at which a species was observed, as well who made the observation, "
                       "who identified the species, and other information related to the observation event."
    }
    ask_an_expert = {
        "name": "ask_an_expert",
        "description": "If none of the other tools satisfy the user's request, ask an expert for help."
    }
    # Unused for now:
    wrong_topic = {
        "name": "wrong_topic",
        "description": "Signals that the user's query is not related to biodiversity, including living organisms, "
                       "species, taxonomy, "
                       "biological specimens, specimen collections, or people who collect them, or any of the "
                       "available tools."
    }


ALL_FUNCTIONS = [
    Functions.retrieve_species_occurrence_records,
    Functions.ask_an_expert
]


def ask_llm_to_call_a_function(prompt, *functions):
    return client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
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


@pytest.mark.skip("This is just reference code")
def test_user_wants_records():
    for _ in repeat(SAMPLE_SIZE):
        resp = ask_llm_to_call_a_function("Find Ursus arctos occurrence records", *ALL_FUNCTIONS)
        assert resp.choices[0].message.function_call.name == "retrieve_species_occurrence_records"


@pytest.mark.skip("This is just reference code")
def test_user_wants_an_expert_on_topic():
    for _ in repeat(SAMPLE_SIZE):
        resp = ask_llm_to_call_a_function("What's the difference between bears and bees?", *ALL_FUNCTIONS)
        assert resp.choices[0].message.function_call is None or resp.choices[
            0].message.function_call.name == "ask_an_expert"


@pytest.mark.skip("This is just reference code")
def test_user_wants_an_expert_off_topic():
    for _ in repeat(SAMPLE_SIZE):
        resp = ask_llm_to_call_a_function("What's your name?", *ALL_FUNCTIONS)
        assert resp.choices[0].message.function_call is None or resp.choices[
            0].message.function_call.name == "ask_an_expert"


@pytest.mark.skip("This is just reference code")
def test_on_topic():
    for _ in repeat(SAMPLE_SIZE):
        resp = ask_llm_to_call_a_function(
            "Is this prompt related to scientific knowledge of living organisms?\n\nPrompt:\"What's the difference "
            "between bears and bees?\"",
            {"name": "yes", "description": "Respond \"yes\" to the question"},
            {"name": "no", "description": "Respond \"no\" to the question"}
        )
        assert resp.choices[0].message.function_call.name == "yes"


@pytest.mark.skip("This is just reference code")
def test_off_topic():
    for _ in repeat(SAMPLE_SIZE):
        resp = ask_llm_to_call_a_function(
            "Is this prompt related to scientific knowledge of living organisms?\n\nPrompt: \"Do you like bears?\"",
            {"name": "yes", "description": "Respond \"yes\" to the question"},
            {"name": "no", "description": "Respond \"no\" to the question"}
        )
        assert resp.choices[0].message.function_call.name == "no"


@pytest.mark.skip("This is just reference code")
def test_species_presence_in_country():
    for _ in repeat(SAMPLE_SIZE):
        resp = ask_llm_to_call_a_function(
            "Is this prompt related to scientific knowledge of living organisms?\n\nPrompt: \"Do you like bears?\"",
            {"name": "yes", "description": "Respond \"yes\" to the question"},
            {"name": "no", "description": "Respond \"no\" to the question"}
        )
        assert resp.choices[0].message.function_call.name == "no"


@pytest.mark.skip("This is just reference code")
def test_idigbio_wiki_search():
    """Find, quote, and relate information from iDigBio's wiki"""


@pytest.mark.skip("This is just reference code")
def test_summarize_habitat_notes():
    """Summarize habitat notes across a set of occurrence records"""


@pytest.mark.skip("This is just reference code")
def test_refine_idigbio_search_query():
    """Conversationally refine a search query"""


@pytest.mark.skip("This is just reference code")
def test_compile_list_of_species():
    """From a list of records, list out the unique species that are represented"""


@pytest.mark.skip("This is just reference code")
def test_detect_species_synonyms():
    """Decide whether two scientific names identify the same species"""


@pytest.mark.skip("This is just reference code")
def test_multistep_reasoning():
    """Invoke a sequence of tools to fulfill user queries"""


@pytest.mark.skip("This is just reference code")
def test_request_dataset_download_by_polling():
    """
    Generate a DarwinCore archive using the iDigBio Download API, wait for it to finish.
    https://www.idigbio.org/wiki/index.php/IDigBio_Download_API
    """


@pytest.mark.skip("This is just reference code")
def test_request_dataset_download_by_email():
    """
    Generate a DarwinCore archive using the iDigBio Download API, request delivery by email.
    https://www.idigbio.org/wiki/index.php/IDigBio_Download_API
    """
