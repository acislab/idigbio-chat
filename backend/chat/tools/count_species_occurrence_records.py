from collections.abc import Iterator

import requests

import idigbio_util
import search
from chat.chat_util import present_results
from chat.conversation import Conversation, Message, AiProcessingMessage, AiChatMessage
from chat.stream_util import StreamedLast
from chat.tools.tool import Tool
from nlp.agent import Agent


class CountSpeciesOccurrenceRecords(Tool):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "count_species_occurrence_records",
        "description": "Counts the number of records in iDigBio matching the user's search criteria."
    }

    verbal_return_type = "the number of species occurrence records that match the user's search criteria"

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        api_query = StreamedLast(_ask_llm_to_generate_search_query(agent, history, request))

        yield AiProcessingMessage("Searching for records...", api_query)
        yield present_results(agent, history, self.verbal_return_type)

        params = api_query.get()
        if "rq" in params:
            url, count = _get_record_count(params["rq"])
            yield AiChatMessage(f"There are {count} matching records [in iDigBio]({url})")
        else:
            yield AiChatMessage("I couldn't find what you are looking for, please try again.")


def _ask_llm_to_generate_search_query(agent: Agent, history: Conversation, request: str) -> Iterator[str]:
    params = search.functions.generate_rq.search_species_occurrence_records(agent,
                                                                            history.render_to_openai(request=request))
    yield params


def _get_record_count(rq: dict) -> (str, int):
    url_params = idigbio_util.url_encode_params({"rq": rq, "count": 1})
    query_url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"
    res = requests.get(query_url)
    return query_url, res.json()["itemCount"]
