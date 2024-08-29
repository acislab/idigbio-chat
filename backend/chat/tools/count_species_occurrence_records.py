from collections.abc import Iterator

from chat import conversation
from chat.conversation import Conversation, Message, AiProcessingMessage, present_results, \
    ask_llm_to_generate_search_query
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
            params = ask_llm_to_generate_search_query(agent, history, request)
            return (s for s in conversation.stream_summary_of_idigbio_search_results(params))

        results = StreamedString(get_results())
        
        yield AiProcessingMessage("Searching for records...", results)
        yield present_results(agent, history, request, results)
