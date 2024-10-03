from collections.abc import Iterator

from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.conversation import Conversation
from chat.messages import Message
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.agent import Agent


class SearchSpeciesOccurrenceRecords(Tool):
    schema = {
        "name": "search_species_occurrence_records",
        "description": """Searches for species occurrence records using the iDigBio Portal or the iDigBio records 
        API. Returns the total number of records that were found, the URL used to call the iDigBio Records API to 
        perform the search, and a URL to view the results in the iDigBio Search Portal."""
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioRecordsSearch(agent, history, request)
        yield search.make_message()
        yield present_results(agent, history, request, search.summarize())
