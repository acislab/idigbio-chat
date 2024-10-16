import instructor
import openai
import pytest
import requests
from dotenv import load_dotenv

from backend.schema.idigbio.api import IDigBioRecordsApiParameters
from tests.test_util import repeat

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI())

SAMPLE_SIZE = 1


def ask_llm_to_generate_search_query(prompt: str) -> IDigBioRecordsApiParameters:
    return client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioRecordsApiParameters,
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


@pytest.mark.skip("This is just reference code")
def test_simple_search_shorthand():
    for _ in repeat(SAMPLE_SIZE):
        q = ask_llm_to_generate_search_query("Ursus arctos in North America")
        result = q.model_dump(exclude_none=True, by_alias=True)
        assert result["rq"] == {"continent": "North America", "scientificname": "Ursus arctos"}


@pytest.mark.skip("This is just reference code")
def test_simple_search():
    for _ in repeat(SAMPLE_SIZE):
        q = ask_llm_to_generate_search_query("Show Ursus arctos occurrences in North America")
        result = q.model_dump(exclude_none=True, by_alias=True)
        assert result["rq"] == {"continent": "North America", "scientificname": "Ursus arctos"}


@pytest.mark.skip("This is just reference code")
def test_search_by_higher_taxonomy():
    for _ in repeat(SAMPLE_SIZE):
        q = ask_llm_to_generate_search_query("Retrieve records for the family Ursidae")
        result = q.model_dump(exclude_none=True, by_alias=True)
        assert result["rq"] == {"family": "Ursidae"}


@pytest.mark.skip("This is just reference code")
def test_naive_search_by_common_name():
    q = ask_llm_to_generate_search_query("Retrieve records for all bear species")
    result = q.model_dump(exclude_none=True, by_alias=True)

    records = requests.post("https://search.idigbio.org/v2/search/records", json=result).json()
    for r in records["items"]:
        assert r["indexTerms"]["family"] == "ursidae"

    assert records["itemCount"] == 1  # Not great!
