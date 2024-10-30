from attr import dataclass
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying

import search
from chat.content_streams import StreamedString
from chat.conversation import Conversation
from chat.processes.process import Process
from chat.utils.json import make_pretty_json_string
from idigbio_util import query_idigbio_api, make_idigbio_api_url, make_idigbio_portal_url
from nlp.ai import AI, StopOnTerminalErrorOrMaxAttempts, AIGenerationException
from schema.idigbio.api import IDigBioRecordsApiParameters


@dataclass
class Results(dict):
    params: dict
    record_count: int
    api_query_url: str
    portal_url: str


class IDigBioRecordsSearch(Process):
    process_summary = "Searching for records..."

    def __run__(self, agent: AI, history=Conversation([]), request: str = None) -> StreamedString:
        try:
            params = _generate_records_search_parameters(agent, history, request)
        except AIGenerationException as e:
            yield self.note(e.message)
            return

        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```")

        records_api_url = make_idigbio_api_url("/v2/search/records")
        self.note(f"Sending a POST request to the iDigBio records API at {records_api_url}")

        response_code, success, response_data = query_idigbio_api("/v2/search/records", params)
        record_count = response_data.get("itemCount", 0)

        if success:
            self.note(f"Response code: {response_code}")
        else:
            yield self.note(f"\n\nResponse code: {response_code} - something went wrong!")
            return

        api_query_url = make_idigbio_api_url("/v2/search/records", params)
        yield f"\n\n[View {record_count} matching records]({api_query_url})"
        self.note(f"The API query matched {record_count} records in iDigBio using the URL {api_query_url}")

        portal_url = make_idigbio_portal_url(params)
        yield f" | [Show in iDigBio portal]({portal_url})"
        self.note(
            f"The records can be viewed in the iDigBio portal at {portal_url}. The portal shows the records in an "
            f"interactive list and plots them on a map. The raw records returned returned by the API can be found at "
            f"{api_query_url}"
        )

        self.set_results(Results(
            params=params,
            record_count=record_count,
            api_query_url=api_query_url,
            portal_url=portal_url
        ))


def _generate_records_search_parameters(agent: AI, history: Conversation, request: str) -> dict:
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
        raise AIGenerationException(e)

    params = result.model_dump(exclude_none=True, by_alias=True)
    return params
