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


class IDigBioRecordsSearch:
    params: dict
    record_count: int
    records_api_url: str
    portal_url: str
    __results: str | StreamedString

    def __get_results__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        self.params = generate_records_search_parameters(agent, history, request)
        yield f"Generated search parameters:\n```json\n{make_pretty_json_string(self.params)}\n```"

        url_params = idigbio_util.url_encode_params(self.params)
        self.records_api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
        self.record_count, _ = get_record_count(self.records_api_url)
        yield f"\n\n[View {self.record_count} matching records]({self.records_api_url})"

        self.portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
        yield f" | [Show in iDigBio portal]({self.portal_url})"

    def __init__(self, agent: Agent, history=Conversation([]), request: str = None):
        self.__results = self.__get_results__(agent, history, request)

    def make_message(self) -> Message:
        return AiProcessingMessage("Searching for records...", self.__results)

    def summarize(self) -> str:
        return SUMMARY.format(
            pretty_params=make_pretty_json_string(self.params),
            records_api_url=self.records_api_url,
            portal_url=self.portal_url,
            record_count=self.record_count
        )
