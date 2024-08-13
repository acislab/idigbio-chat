from chat.conversation import Conversation
from nlp.agent import Agent
import search

from chat.tools.tool import Tool


class SearchSpeciesOccurrenceRecords(Tool):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "search_species_occurrence_records",
        "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                       "geographic distribution."
    }

    def call(self, agent: Agent, request: str, conversation=Conversation([]), state=None):
        return ask_llm_to_generate_search_query(agent, request)


def ask_llm_to_generate_search_query(agent: Agent, request: str):
    return search.api.generate_rq(agent, {
        "input": request
    })
