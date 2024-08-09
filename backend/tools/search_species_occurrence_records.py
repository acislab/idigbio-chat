import idigbio_util
from chat.agent import Agent
from chat.types import Conversation
from idigbio_records_api_schema import LLMQueryOutput

from tools.tool import Tool


class SearchSpeciesOccurrenceRecords(Tool):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "search_species_occurrence_records",
        "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                       "geographic distribution."
    }

    def call(self, agent: Agent, conversation: Conversation):
        return ask_llm_to_generate_search_query(agent, conversation)


def ask_llm_to_generate_search_query(agent: Agent, conversation: Conversation):
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=LLMQueryOutput,
        messages=conversation,
    )

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
