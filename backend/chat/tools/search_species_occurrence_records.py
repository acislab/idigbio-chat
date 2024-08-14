from collections.abc import Iterator

import search
from chat.chat_util import present_results
from chat.conversation import Conversation, AiMessage, Message
from chat.tools.tool import Tool
from nlp.agent import Agent


class SearchSpeciesOccurrenceRecords(Tool):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "search_species_occurrence_records",
        "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                       "geographic distribution."
    }

    verbal_return_type = "a list of records"

    def call(self, agent: Agent, request: str, history=Conversation([]), state=None) -> Iterator[Message]:
        yield present_results(agent, history, self.verbal_return_type)

        res = _ask_llm_to_generate_search_query(agent, request)
        yield AiMessage({"rq": res["rq"]})


def _ask_llm_to_generate_search_query(agent: Agent, request: str):
    return search.api.generate_rq(agent, {
        "input": request
    })
