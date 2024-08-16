import json
from collections.abc import Iterator

import search
from chat.chat_util import present_results
from chat.conversation import Conversation, Message, AiMapMessage, AiProcessingMessage
from chat.stream_util import StreamedContent, StreamedLast
from chat.tools.tool import Tool
from nlp.agent import Agent


class ShowMapOfSpeciesOccurrences(Tool):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "show_map_of_species_occurrences",
        "description": "Shows an interactive map of species occurrences described in records from iDigBio."
    }

    verbal_return_type = "a map of recorded species occurrences"

    def call(self, agent: Agent, request: str, history=Conversation([]), state=None) -> Iterator[Message]:
        api_query = StreamedLast(_ask_llm_to_generate_search_query(agent, history, request))

        yield AiProcessingMessage("Searching for records...", api_query)
        yield present_results(agent, history, self.verbal_return_type)
        yield AiMapMessage(api_query)


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation, request: str) -> Iterator[str]:
    rq = search.functions.generate_rq.search_species_occurrence_records(agent, history.render_to_openai())
    yield rq
