from collections.abc import Iterator

from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.conversation import Conversation
from chat.messages import Message
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.agent import Agent


class SearchMediaRecords(Tool):
    schema = {
        "name": "search_media_records",
        "description": """Searches for media records (like images) using the iDigBio Portal or the iDigBio media API. 
        Returns the total number of media records that were found, the URL used to call the iDigBio media API to 
        perform the search, and a URL to view the results in the iDigBio Search Portal."""
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioRecordsSearch(agent, history, request)
        yield search.make_message()
        yield present_results(agent, history, request, search.summarize())
