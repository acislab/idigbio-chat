from collections.abc import Iterator

import requests

import idigbio_util
import search
from chat import chat_util, conversation
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiProcessingMessage, present_results
from chat.stream_util import StreamedString
from chat.tools.tool import Tool
from nlp.agent import Agent


class CountSpeciesOccurrenceRecords(Tool):
    schema = {
        "name": "count_species_occurrence_records",
        "description": "Counts the number of records in iDigBio matching the user's search criteria. Returns links to "
                       "call the iDigBio Records API and to the iDigBio Search Portal."
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        results = StreamedString(conversation.stream_summary_of_idigbio_search_results(agent, history, request))
        yield AiProcessingMessage("Searching for records...", results)
        yield present_results(agent, history, request, results)
