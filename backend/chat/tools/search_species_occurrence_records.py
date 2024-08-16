import json
from collections.abc import Iterator

import idigbio_util
import search
from chat.chat_util import present_results
from chat.conversation import Conversation, Message, AiMapMessage, AiProcessingMessage, AiChatMessage
from chat.stream_util import StreamedContent, StreamedLast
from chat.tools.tool import Tool
from nlp.agent import Agent


class SearchSpeciesOccurrenceRecords(Tool):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "search_species_occurrence_records",
        "description": "Shows a list of species occurrence records in iDigBio Portal and through the iDigBio records "
                       "API."
    }

    verbal_return_type = "a list of records"

    def call(self, agent: Agent, request: str, history=Conversation([]), state=None) -> Iterator[Message]:
        query_params = StreamedLast(_ask_llm_to_generate_search_query(agent, history))

        yield AiProcessingMessage("Searching for records...", query_params)
        yield present_results(agent, history, self.verbal_return_type)

        url_params = idigbio_util.url_encode_params(query_params.get())

        yield AiChatMessage(f"[iDigBio portal search](https://beta-portal.idigbio.org/portal/search?{url_params})")
        yield AiChatMessage(f"[iDigBio records API search](https://search.idigbio.org/v2/search/records?{url_params})")


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation):
    params = search.functions.generate_rq.search_species_occurrence_records(agent, history.render_to_openai())
    yield params
