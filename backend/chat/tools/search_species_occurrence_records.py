from collections.abc import Iterator

import idigbio_util
import search
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiProcessingMessage, AiChatMessage
from chat.tools.tool import Tool
from nlp.agent import Agent


class SearchSpeciesOccurrenceRecords(Tool):
    schema = {
        "name": "search_species_occurrence_records",
        "description": """Searches for species occurrence records using the iDigBio Portal or the iDigBio records 
        API. Returns the total number of records that were found, the URL used to call the iDigBio Records API to 
        perform the search, and a URL to view the results in the iDigBio Search Portal."""
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        params = next(_ask_llm_to_generate_search_query(agent, history, request))

        yield AiProcessingMessage("Searching for records...", make_pretty_json_string(params))

        url_params = idigbio_util.url_encode_params(params)

        yield AiChatMessage(f"[iDigBio portal search](https://beta-portal.idigbio.org/portal/search?{url_params})")
        yield AiChatMessage(f"[iDigBio records API search](https://search.idigbio.org/v2/search/records?{url_params})")


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation, request: str) -> Iterator[dict]:
    params = search.functions.generate_rq.search_species_occurrence_records(agent,
                                                                            history.render_to_openai(request=request))
    yield params
