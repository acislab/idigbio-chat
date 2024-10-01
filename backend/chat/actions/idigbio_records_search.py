import requests
from attr import dataclass

import idigbio_util
import search
from chat.chat_util import make_pretty_json_string
from chat.conversation import Message, Conversation, AiProcessingMessage
from chat.stream_util import StreamedString
from nlp.agent import Agent
from schema.idigbio.api import IDigBioRecordsApiParameters

SUMMARY = """\
Generated the following search parameters to find species occurrence records in iDigBio:
```json
{pretty_params}
```

Querying the iDigBio records API with URL {records_api_url} returned {record_count} matching records.

The records can be viewed in the iDigBio portal at {portal_url}. The portal shows the records in an interactive list 
and plots them on a map.
"""


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
class IDigBioRecordsSearchResults:
    params: dict
    record_count: int
    records_api_url: str
    portal_url: str


class IDigBioRecordsSearch:
    __results: IDigBioRecordsSearchResults
    __content: StreamedString

    @property
    def results(self):
        self.__content.get()
        return self.__results

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        params = _generate_records_search_parameters(agent, history, request)
        yield f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```"

        url_params = idigbio_util.url_encode_params(params)
        records_api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
        record_count = _query_search_api(records_api_url)
        yield f"\n\n[View {record_count} matching records]({records_api_url})"

        portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
        yield f" | [Show in iDigBio portal]({portal_url})"

        self.__results = IDigBioRecordsSearchResults(params, record_count, records_api_url, portal_url)

    def __init__(self, agent: Agent, history=Conversation([]), request: str = None):
        self.__content = StreamedString(self.__run__(agent, history, request))

    def make_message(self) -> Message:
        def think():
            yield self.summarize()

        return AiProcessingMessage("Searching for records...", self.__content, StreamedString(think()))

    def summarize(self) -> str:
        r = self.results
        return SUMMARY.format(
            pretty_params=make_pretty_json_string(r.params),
            records_api_url=r.records_api_url,
            portal_url=r.portal_url,
            record_count=r.record_count
        )
