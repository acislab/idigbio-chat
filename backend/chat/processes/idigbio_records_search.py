import requests
from attr import dataclass
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying

import idigbio_util
import search
from chat.content_streams import StreamedString
from chat.conversation import Conversation
from chat.processes.process import Process
from chat.utils.json import make_pretty_json_string
from nlp.agent import Agent, StopOnTerminalErrorOrMaxAttempts, AgentGenerationException
from schema.idigbio.api import IDigBioRecordsApiParameters


@dataclass
class Results(dict):
    params: dict
    record_count: int
    records_api_url: str
    portal_url: str


class IDigBioRecordsSearch(Process):
    process_summary = "Searching for records..."

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        try:
            params = _generate_records_search_parameters(agent, history, request)
        except AgentGenerationException as e:
            yield self.note(e.message)
            return

        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```")

        url_params = idigbio_util.url_encode_params(params)
        records_api_url = f"https://search.idigbio.org/v2/search/records?{url_params}"
        self.note(f"Querying the iDigBio records API with URL {records_api_url}")
        record_count = _query_search_api(records_api_url)
        yield f"\n\n[View {record_count} matching records]({records_api_url})"
        self.note(f"The API query matched {record_count} records in iDigBio")

        portal_url = f"https://portal.idigbio.org/portal/search?{url_params}"
        yield f" | [Show in iDigBio portal]({portal_url})"
        self.note(
            f"The records can be viewed in the iDigBio portal at {portal_url}. The portal shows the records in an "
            f"interactive list and plots them on a map.")

        self.set_results(Results(
            params=params,
            record_count=record_count,
            records_api_url=records_api_url,
            portal_url=portal_url
        ))


def _query_search_api(query_url: str) -> (int, dict):
    res = requests.get(query_url)
    return res.json()["itemCount"]


def _generate_records_search_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    try:
        result = agent.client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            response_model=IDigBioRecordsApiParameters,
            messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT,
                                              request=request),
            max_retries=Retrying(stop=StopOnTerminalErrorOrMaxAttempts(3))
        )
    except InstructorRetryException as e:
        raise AgentGenerationException(e)

    params = result.model_dump(exclude_none=True, by_alias=True)
    return params
