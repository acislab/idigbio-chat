from attr import dataclass

import idigbio_util
from chat.chat_util import make_pretty_json_string
from chat.conversation import Message, generate_records_search_parameters, Conversation, get_record_count, \
    AiProcessingMessage
from chat.stream_util import StreamedString
from nlp.agent import Agent

SUMMARY = """\
Generated the following search parameters to find species occurrence records in iDigBio:
```json
{pretty_params}
```

Querying the iDigBio records API with URL {records_api_url} returned {record_count} matching records.

The records can be viewed in the iDigBio portal at {portal_url}. The portal shows the records in an interactive list 
and plots them on a map.
"""


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
        params = generate_records_search_parameters(agent, history, request)
        yield f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```"

        url_params = idigbio_util.url_encode_params(params)
        records_api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
        record_count, _ = get_record_count(records_api_url)
        yield f"\n\n[View {record_count} matching records]({records_api_url})"

        portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
        yield f" | [Show in iDigBio portal]({portal_url})"

        self.__results = IDigBioRecordsSearchResults(params, record_count, records_api_url, portal_url)

    def __init__(self, agent: Agent, history=Conversation([]), request: str = None):
        self.__content = StreamedString(self.__run__(agent, history, request))

    def make_message(self) -> Message:
        return AiProcessingMessage("Searching for records...", self.__content)

    def summarize(self) -> str:
        r = self.results
        return SUMMARY.format(
            pretty_params=make_pretty_json_string(r.params),
            records_api_url=r.records_api_url,
            portal_url=r.portal_url,
            record_count=r.record_count
        )
