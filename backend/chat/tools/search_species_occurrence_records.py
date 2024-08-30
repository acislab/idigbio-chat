from collections.abc import Iterator

import idigbio_util
from chat import conversation
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiProcessingMessage, present_results, \
    ask_llm_to_generate_search_query, get_record_count
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
        def get_results():
            params = ask_llm_to_generate_search_query(agent, history, request)
            yield f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```"

            url_params = idigbio_util.url_encode_params(params)
            api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
            yield f"\n\nRetrieve records using the iDigBio records API [here]({api_url})"

            portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
            yield f"\n\nView results in the iDigBio portal [here]({portal_url})"

            count = get_record_count(api_url)
            yield f"\n\nTotal number of matching records: {count}"

        results = StreamedString(get_results())

        yield AiProcessingMessage("Searching for records...", results)
        yield present_results(agent, history, request, results)
