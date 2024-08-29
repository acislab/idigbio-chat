from collections.abc import Iterator

from chat import conversation
from chat.conversation import Conversation, Message, AiProcessingMessage, present_results
from chat.stream_util import StreamedString
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
        results = StreamedString(conversation.stream_summary_of_idigbio_search_results(agent, history, request))
        yield AiProcessingMessage("Searching for records...", results)
        yield present_results(agent, history, request, results)
