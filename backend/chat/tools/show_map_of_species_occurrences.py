from collections.abc import Iterator

from chat.plans import DataType
from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.conversation import Conversation
from chat.messages import Message, AiMapMessage
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI

DESCRIPTION = """\
Shows an interactive map of species occurrences described in records served by iDigBio. The map is visualized using 
the Leaflet JavaScript library (https://leafletjs.com/).
"""


class ShowMapOfSpeciesOccurrences(Tool):
    name = "show_map_of_species_occurrences"
    description = DESCRIPTION
    output = DataType.species_occurrence_map

    def call(self, ai: AI, conversation: Conversation, request: str, state: dict) -> Iterator[Message]:
        search = IDigBioRecordsSearch(ai, conversation, request)
        yield search.make_message()

        if search.results.record_count > 0:
            yield AiMapMessage(search.results.params)
        else:
            yield present_results(ai, conversation, request, search.describe() +
                                  f"\n\nPlease explain to the user that because no records were found, no map will be "
                                  f"shown. Be as concise as possible.")
