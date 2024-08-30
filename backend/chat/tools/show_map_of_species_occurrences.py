from collections.abc import Iterator

import idigbio_util
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiMapMessage, AiProcessingMessage, \
    present_results, get_record_count, generate_records_search_parameters
from chat.stream_util import StreamedString
from chat.tools.tool import Tool
from nlp.agent import Agent


class ShowMapOfSpeciesOccurrences(Tool):
    schema = {
        "name": "show_map_of_species_occurrences",
        "description": "Shows an interactive map of species occurrences described in records served by iDigBio. The "
                       "map is visualized using the Leaflet JavaScript library (https://leafletjs.com/)."
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        params_box = [{}]
        count_box = [0]

        def get_results():
            params = generate_records_search_parameters(agent, history, request)
            params_box[0] = params

            yield f"```Generated search parameters:\njson\n{make_pretty_json_string(params)}\n```"

            url_params = idigbio_util.url_encode_params(params)
            api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
            yield f"\n\nRetrieve records using the iDigBio records API [here]({api_url})"

            portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
            yield f"\n\nView results in the iDigBio portal [here]({portal_url})"

            count, _ = get_record_count(api_url)
            count_box[0] = count
            yield f"\n\nTotal number of matching records in iDigBio: {count}"

        results = StreamedString(get_results())

        yield AiProcessingMessage("Searching for records...", results)

        count = count_box[0]
        if count > 0:
            yield AiMapMessage(params_box[0])
        else:
            results = results.get() + (
                f"\n\nPlease explain to the user that because no records were found, no map will be "
                f"shown. Be as concise as possible.")
            yield present_results(agent, history, request, results)
