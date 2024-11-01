from collections.abc import Iterator

from chat.plans import DataType
from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.conversation import Conversation
from chat.messages import Message
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI

DESCRIPTION = """\
Searches for species occurrence records using the iDigBio Portal or the iDigBio records API. Returns the total number 
of records that were found, the URL used to call the iDigBio Records API to perform the search, and a URL to view the 
results in the iDigBio Search Portal.
"""


class SearchSpeciesOccurrenceRecords(Tool):
    name = "search_species_occurrence_records"
    description = DESCRIPTION
    output = DataType.species_occurrence_records

    def call(self, ai: AI, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioRecordsSearch(ai, history, request)
        yield search.make_message()
        yield present_results(ai, history, request, search.describe())
