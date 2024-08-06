import instructor
import openai
from dotenv import load_dotenv

import idigbio_util
from idigbio_records_api_schema import LLMQueryOutput

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI())


def ask_llm_to_generate_search_query(prompt: str):
    result = __generate_query__(prompt)

    params = result.model_dump(exclude_none=True)
    url_params = idigbio_util.url_encode_params(params)

    return [
        {
            "type": "idigbio-search-parameters",
            "data": params
        },
        {
            "type": "url",
            "data": {
                "name": "iDigBio Portal Search",
                "url": f"https://beta-portal.idigbio.org/portal/search?{url_params}"
            }
        },
        {
            "type": "url",
            "data": {
                "name": "iDigBio Search API",
                "url": f"https://search.idigbio.org/v2/search/records?{url_params}"
            }
        }
    ]


def __generate_query__(prompt: str) -> LLMQueryOutput:
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
