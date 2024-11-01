from collections.abc import Iterator

from chat.conversation import Conversation
from chat.messages import Message
from chat.plans import DataType
from chat.processes.idigbio_media_search import IDigBioMediaSearch
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI

DESCRIPTION = """\
Searches for media records (like images) using the iDigBio Portal or the iDigBio media API. Returns the total number 
of media records that were found, the URL used to call the iDigBio media API to perform the search, and a URL to view 
the results in the iDigBio Search Portal.
"""


class SearchMediaRecords(Tool):
    name = "search_media_records"
    description = DESCRIPTION
    output = DataType.species_media_records

    def call(self, ai: AI, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioMediaSearch(ai, history, request)
        yield search.make_message()
        yield present_results(ai, history, request, search.describe())
