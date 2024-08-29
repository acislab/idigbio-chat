from collections.abc import Iterator

import search
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiMapMessage, AiProcessingMessage, present_results
from chat.tools.tool import Tool
from nlp.agent import Agent


class ShowMapOfSpeciesOccurrences(Tool):
    schema = {
        "name": "show_map_of_species_occurrences",
        "description": "Shows an interactive map of species occurrences described in records served by iDigBio. The "
                       "map is visualized using the Leaflet JavaScript library (https://leafletjs.com/)."
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        params = next(_ask_llm_to_generate_search_query(agent, history, request))

        yield AiProcessingMessage("Searching for records...", make_pretty_json_string(params))
        yield AiMapMessage(params)


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation, request: str) -> Iterator[dict]:
    params = search.functions.generate_rq.search_species_occurrence_records(agent,
                                                                            history.render_to_openai(request=request))
    yield params
