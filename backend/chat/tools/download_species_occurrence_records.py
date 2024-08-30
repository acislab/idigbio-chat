from collections.abc import Iterator

import requests

import idigbio_util
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation, Message, AiProcessingMessage, present_results, \
    get_record_count, generate_records_download_parameters
from chat.stream_util import StreamedString
from chat.tools.tool import Tool
from nlp.agent import Agent

live = True


class DownloadSpeciesOccurrenceRecords(Tool):
    schema = {
        "name": "download_species_occurrence_records",
        "description": """Begins a search for species occurrence records using the iDigBio records API. Once the 
        search is completed, the results are packaged as a DarwinCore Archive zip file and sent to a specified email 
        address."""
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        success_box = [False]

        def get_results():
            params = generate_records_download_parameters(agent, history, request)
            yield f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```"

            url_params = idigbio_util.url_encode_params(params)
            api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
            yield f"\n\nRetrieve records using the iDigBio records API [here]({api_url})"

            portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
            yield f"\n\nView results in the iDigBio portal [here]({portal_url})"

            count, _ = get_record_count(api_url)
            yield f"\n\nTotal number of matching records in iDigBio: {count}"

            yield f"\n\nSending download request... "

            if live:
                response_code, success = send_download_request(url_params)
            else:
                response_code, success = 200, True

            yield f"Response code: {response_code}"
            if success:
                yield f"\n\nDownload request sent to {params['email']}!"
            else:
                yield f"\n\nError! Something went wrong."

            success_box[0] = success

        results = StreamedString(get_results())

        yield AiProcessingMessage("Generating download request...", results)

        if success_box[0]:
            success_message = (
                "\n\nPlease inform the user that the download request was sent and they should receive an email when "
                "their download is ready."
            )
        else:
            success_message = "\n\nPlease inform the user that something went wrong with the download request.."

        yield present_results(agent, history, request, results.get() + success_message)


def send_download_request(url_params):
    res = requests.get(f"https://search.idigbio.org/v2/download?{url_params}")
    return res.status_code, res.ok
