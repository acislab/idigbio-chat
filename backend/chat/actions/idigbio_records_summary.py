from typing import Iterable

import requests
from attr import dataclass

import idigbio_util
import search
from chat.actions.action import Action
from chat.chat_util import make_pretty_json_string
from chat.conversation import Conversation
from chat.stream_util import StreamedString
from nlp.agent import Agent
from schema.idigbio.api import IDigBioSummaryApiParameters

DEFAULT_NUM_TOP_COUNTS = 10
MAX_NUM_TOP_COUNTS = 100


@dataclass
class Results(dict):
    params: dict
    total_count: int
    top_counts: dict
    full_summary_api_url: str
    limited_summary_api_url: str


class IDigBioRecordsSummary(Action):
    process_summary = "Searching for records..."

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        params = _generate_records_summary_parameters(agent, history, request)

        if "top_fields" not in params:
            params |= {"top_fields": "scientificname"}
        top_fields = params["top_fields"]

        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```")

        url_params = idigbio_util.url_encode_params(params)
        full_summary_api_url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"

        test_params = params.copy()
        if "count" not in test_params:
            test_params |= {"count": DEFAULT_NUM_TOP_COUNTS}
        elif test_params["count"] > MAX_NUM_TOP_COUNTS:
            test_params["count"] = MAX_NUM_TOP_COUNTS
        limited_summary_api_url = f"https://search.idigbio.org/v2/summary/top/records?{url_params}"

        self.note(f"Querying the iDigBio summary API with URL {full_summary_api_url}")
        if "count" not in params:
            self.note(f"Warning: count not specified, only checking the top {DEFAULT_NUM_TOP_COUNTS} counts.")
        elif params["count"] > MAX_NUM_TOP_COUNTS:
            self.note(f"\nWarning: only checking the top {MAX_NUM_TOP_COUNTS} counts.")

        total_count, top_counts = _query_summary_api(limited_summary_api_url)
        yield f"\n\n[View summary of {total_count} records]({full_summary_api_url})"
        self.note(f"The API query matched {total_count} total records in iDigBio")

        counts_table = "".join(_stream_record_counts_as_markdown_table(top_counts))
        self.note(f"Breakdown of counts by {top_fields} in descending order:\n\n{counts_table}")

        self.set_results(Results(
            params=params,
            total_count=total_count,
            top_counts=top_counts,
            full_summary_api_url=full_summary_api_url,
            limited_summary_api_url=limited_summary_api_url
        ))


def _query_summary_api(query_url: str) -> (int, dict):
    res = requests.get(query_url)
    return res.json()["itemCount"], res.json()


def _generate_records_summary_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioSummaryApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True)
    return params


def _stream_record_counts_as_markdown_table(counts) -> Iterable[str]:
    top_field = [x for x in counts if x != "itemCount"][0]

    yield f"| {top_field} | count |\n"
    yield "|-|-|\n"
    for row in (f"| {k} | {v['itemCount']} |\n" for k, v in counts[top_field].items()):
        yield row
