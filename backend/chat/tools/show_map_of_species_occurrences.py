from collections.abc import Iterator

from chat import conversation
from chat.conversation import Conversation, Message, AiMapMessage, AiProcessingMessage, \
    ask_llm_to_generate_search_query
from chat.stream_util import StreamedString
from chat.tools.tool import Tool
from nlp.agent import Agent


class ShowMapOfSpeciesOccurrences(Tool):
    schema = {
        "name": "show_map_of_species_occurrences",
        "description": "Shows an interactive map of species occurrences described in records served by iDigBio. The "
                       "map is visualized using the Leaflet JavaScript library (https://leafletjs.com/)."
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        params_box = [{}]

        def get_results():
            params = ask_llm_to_generate_search_query(agent, history, request)
            params_box[0] = params
            return (s for s in conversation.stream_summary_of_idigbio_search_results(params))

        results = StreamedString(get_results())

        yield AiProcessingMessage("Searching for records...", results)
        yield AiMapMessage(params_box[0])
