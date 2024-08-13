import instructor
import openai
import requests
from dotenv import load_dotenv

from backend.schema.idigbio.records_api import LLMQueryOutput
from tests.test_util import repeat

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI())

SAMPLE_SIZE = 1


def ask_llm_to_generate_search_query(prompt: str) -> LLMQueryOutput:
    return client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=LLMQueryOutput,
        messages=[
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )


def test_simple_search_shorthand():
    for _ in repeat(SAMPLE_SIZE):
        q = ask_llm_to_generate_search_query("Ursus arctos in North America")
        result = q.model_dump(exclude_none=True)
        assert result["rq"] == {"continent": "North America", "scientificname": "Ursus arctos"}


def test_simple_search():
    for _ in repeat(SAMPLE_SIZE):
        q = ask_llm_to_generate_search_query("Show Ursus arctos occurrences in North America")
        result = q.model_dump(exclude_none=True)
        assert result["rq"] == {"continent": "North America", "scientificname": "Ursus arctos"}


def test_search_by_higher_taxonomy():
    for _ in repeat(SAMPLE_SIZE):
        q = ask_llm_to_generate_search_query("Retrieve records for the family Ursidae")
        result = q.model_dump(exclude_none=True)
        assert result["rq"] == {"family": "Ursidae"}


def test_naive_search_by_common_name():
    q = ask_llm_to_generate_search_query("Retrieve records for all bear species")
    result = q.model_dump(exclude_none=True)

    records = requests.post("https://search.idigbio.org/v2/search/records", json=result).json()
    for r in records["items"]:
        assert r["indexTerms"]["family"] == "ursidae"

    assert records["itemCount"] == 1  # Not great!
