from attr import dataclass

import idigbio_util
from chat.chat_util import make_pretty_json_string
from chat.conversation import Message, Conversation, get_record_count, \
    AiProcessingMessage, generate_records_summary_parameters, stream_record_counts_as_markdown_table
from chat.stream_util import StreamedString
from nlp.agent import Agent

SUMMARY = """\
Generated the following search parameters to count species occurrence records in iDigBio:
```json
{pretty_params}
```

Querying the iDigBio summary API with URL {summary_api_url} returned a total of {total_count} matching records.

Breakdown of counts by {top_fields} in descending order:

{counts_table}\
"""

DEFAULT_NUM_TOP_COUNTS = 10
MAX_NUM_TOP_COUNTS = 100


@dataclass
class IDigBioRecordsSummaryResults:
    params: dict
    total_count: int
    top_counts: dict
    full_summary_api_url: str
    limited_summary_api_url: str


class IDigBioRecordsSummary:
    __results: IDigBioRecordsSummaryResults
    __content: StreamedString

    @property
    def results(self):
        self.__content.get()
        return self.__results

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        params = generate_records_summary_parameters(agent, history, request)

        if "top_fields" not in params:
            params |= {"top_fields": "scientificname"}

        yield f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```"

        url_params = idigbio_util.url_encode_params(params)
        full_summary_api_url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"

        test_params = params.copy()
        if "count" not in test_params:
            test_params |= {"count": DEFAULT_NUM_TOP_COUNTS}
        elif test_params["count"] > MAX_NUM_TOP_COUNTS:
            test_params["count"] = MAX_NUM_TOP_COUNTS
        limited_summary_api_url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"

        total_count, top_counts = get_record_count(limited_summary_api_url)
        yield f"\n\n[View summary of {total_count} records]({full_summary_api_url})"

        self.__results = IDigBioRecordsSummaryResults(
            params=params,
            total_count=total_count,
            top_counts=top_counts,
            full_summary_api_url=full_summary_api_url,
            limited_summary_api_url=limited_summary_api_url
        )

    def __init__(self, agent: Agent, history=Conversation([]), request: str = None):
        self.__content = StreamedString(self.__run__(agent, history, request))

    def make_message(self) -> Message:
        def think():
            yield self.summarize()

        return AiProcessingMessage("Searching for records...", self.__content, StreamedString(think()))

    def summarize(self) -> str:
        r = self.results
        counts_table = "".join(stream_record_counts_as_markdown_table(r.top_counts))
        summary = SUMMARY.format(
            pretty_params=make_pretty_json_string(r.params),
            summary_api_url=r.full_summary_api_url,
            total_count=r.total_count,
            top_fields=r.params["top_fields"],
            counts_table=counts_table
        )

        if "count" not in r.params:
            summary += f"\nWarning: count not specified, only checking the top {DEFAULT_NUM_TOP_COUNTS} counts."
        elif r.params["count"] > MAX_NUM_TOP_COUNTS:
            summary += f"\nWarning: only checking the top {MAX_NUM_TOP_COUNTS} counts."

        return summary
