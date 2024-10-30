from collections.abc import Iterator

from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.conversation import Conversation
from chat.messages import Message, AiMapMessage
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI


class ShowMapOfSpeciesOccurrences(Tool):
    schema = {
        "name": "show_map_of_species_occurrences",
        "description": "Shows an interactive map of species occurrences described in records served by iDigBio. The "
                       "map is visualized using the Leaflet JavaScript library (https://leafletjs.com/)."
    }

    def call(self, ai: AI, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioRecordsSearch(ai, history, request)
        yield search.make_message()

        if search.results.record_count > 0:
            yield AiMapMessage(search.results.params)
        else:
            yield present_results(ai, history, request, search.summarize() +
                                  f"\n\nPlease explain to the user that because no records were found, no map will be "
                                  f"shown. Be as concise as possible.")
