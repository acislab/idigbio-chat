import requests
from attr import dataclass

import idigbio_util
import search
from chat.chat_util import make_pretty_json_string
from chat.conversation import Message, Conversation, AiProcessingMessage
from chat.stream_util import StreamedString
from nlp.agent import Agent
from schema.idigbio.api import IDigBioRecordsApiParameters, IDigBioDownloadApiParameters

live = True


def _generate_records_download_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioDownloadApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True)
    return params


def _send_download_request(url):
    res = requests.get(url)
    return res.status_code, res.ok


def _query_search_api(query_url: str) -> (int, dict):
    res = requests.get(query_url)
    return res.json()["itemCount"]


def _generate_records_search_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioRecordsApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True)
    return params


@dataclass
class IDigBioRecordsDownloadResults:
    params: dict
    download_api_url: str
    success: bool


class IDigBioRecordsDownload:
    __results: IDigBioRecordsDownloadResults
    __content: StreamedString
    __notes: list[str] = []

    @property
    def results(self):
        self.__content.get()
        return self.__results

    def note(self, text: str):
        self.__notes += [text.strip()]
        return text

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        params = _generate_records_download_parameters(agent, history, request)
        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```\n\n")

        self.note(f"Sending download request...")
        url_params = idigbio_util.url_encode_params(params)
        download_api_url = f"https://search.idigbio.org/v2/download?{url_params}"
        if live:
            response_code, success = _send_download_request(download_api_url)
        else:
            response_code, success = 200, True

        yield self.note(f"Response code: {response_code}")

        if success:
            yield " (success)"
            self.note(f"\n\nRequested records download link to be sent to {params['email']}!")
        else:
            yield " (error)"
            self.note(f"\n\nError! Something went wrong.")

        yield f" | [Resend request]({download_api_url})"

        self.__results = IDigBioRecordsDownloadResults(
            params=params,
            download_api_url=download_api_url,
            success=success
        )

    def __init__(self, agent: Agent, history=Conversation([]), request: str = None):
        self.__content = StreamedString(self.__run__(agent, history, request))

    def make_message(self) -> Message:
        def think():
            yield self.summarize()

        return AiProcessingMessage("Generating download request...", self.__content, StreamedString(think()))

    def summarize(self) -> str:
        return "\n\n".join(self.__notes)
