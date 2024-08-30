from collections.abc import Iterator

import idigbio_util
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiProcessingMessage, present_results, \
    ask_llm_to_generate_search_query, get_record_count, stream_record_counts_as_markdown_table
from chat.stream_util import StreamedString
from chat.tools.tool import Tool
from nlp.agent import Agent

DESCRIPTION = """\
Counts the total number of records in iDigBio matching the user's search criteria. Also
breaks the count down by a specified field (default: scientific name) to build top-N lists or to find unique record 
field values that were matched. Counts can be broken down by any of iDigBio's query fields, such as "country" or
"collector".

Here are some examples of building top-N lists:
- List the 10 species that have the most records in a country
- List the 10 countries that have the most records of a species
- List the 10 collectors who have recorded the most occurrences of a species

Here are some examples of finding unique values in matching records:
- List the continents that a species occurs in
- List different scientific names that have the same genus and specific epithet (e.g., scientific names with 
different authors)

Also returns the URL used to collect records counts from the iDigBio Summary API.
"""


class CountSpeciesOccurrenceRecords(Tool):
    schema = {
        "name": "count_species_occurrence_records",
        "description": DESCRIPTION
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        def get_results():
            params = ask_llm_to_generate_search_query(agent, history, request)

            if "top_fields" not in params:
                params |= {"top_fields": "scientificname"}

            if "count" not in params:
                params |= {"count": 10}
            elif params["count"] > 100:
                yield "\n\nWarning: only showing the top 100 counts"

            yield f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```"

            url_params = idigbio_util.url_encode_params(params)
            api_url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"
            yield f"\n\nSee record counts using the iDigBio records API [here]({api_url})"

            portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
            yield f"\n\nView results in the iDigBio portal [here]({portal_url})"

            count, all_counts = get_record_count(api_url)
            yield f"\n\nTotal number of matching records: {count}"

            yield f"\n\nBreakdown of counts by {params['top_fields']} in descending order\n\n"
            for line in stream_record_counts_as_markdown_table(all_counts):
                yield line

        results = StreamedString(get_results())

        yield AiProcessingMessage("Searching for records...", results)
        yield present_results(agent, history, request, results)
