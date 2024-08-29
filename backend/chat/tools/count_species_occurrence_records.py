from collections.abc import Iterator

import requests

import idigbio_util
import search
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
        def get_results():
            params = _ask_llm_to_generate_search_query(agent, history, request)
            yield f"```json\n{make_pretty_json_string(params)}\n```"

            url_params = idigbio_util.url_encode_params(params | {"count": 10})
            url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"
            yield f"\n\nLink to record counts found by the iDigBio records API: {url}"

            count = _get_record_count(url)
            yield f"\n\nTotal number of matching records: {count}"

        results = StreamedString(get_results())
        yield AiProcessingMessage("Searching for records...", results)
        yield present_results(agent, history, request, results)


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation, request: str) -> dict:
    params = search.functions.generate_rq.search_species_occurrence_records(agent,
                                                                            history.render_to_openai(request=request))
    return params


def _get_record_count(query_url: str) -> (str, int):
    res = requests.get(query_url)
    return res.json()["itemCount"]
