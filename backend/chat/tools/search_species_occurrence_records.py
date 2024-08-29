from collections.abc import Iterator

import requests

import idigbio_util
import search
from chat import conversation
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiProcessingMessage, AiChatMessage, present_results
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


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation, request: str) -> dict:
    params = search.functions.generate_rq.search_species_occurrence_records(agent,
                                                                            history.render_to_openai(request=request))
    return params


def _get_record_count(query_url: str) -> (str, int):
    res = requests.get(query_url)
    return res.json()["itemCount"]
