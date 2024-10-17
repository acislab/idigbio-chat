from attr import dataclass
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying

from chat.content_streams import StreamedString
from chat.conversation import Conversation
from chat.processes.process import Process
from chat.utils.json import make_pretty_json_string
from idigbio_util import make_idigbio_api_url, query_idigbio_api
from nlp.agent import Agent, StopOnTerminalErrorOrMaxAttempts, AgentGenerationException
from schema.idigbio.api import IDigBioMediaApiParameters


@dataclass
class Results(dict):
    params: dict
    record_count: int
    api_query_url: str


class IDigBioMediaSearch(Process):
    process_summary = "Searching for media records..."

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        try:
            params = _generate_records_search_parameters(agent, history, request)
        except AgentGenerationException as e:
            yield self.note(e.message)
            return

        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```")

        media_api_url = make_idigbio_api_url("/v2/search/media")
        self.note(f"Sending a POST request to the iDigBio media API at {media_api_url}")

        response_code, success, response_data = query_idigbio_api("/v2/search/media", params)
        record_count = response_data.get("itemCount", 0)

        if success:
            self.note(f"Response code: {response_code}")
        else:
            yield self.note(f"\n\nResponse code: {response_code} - something went wrong!")
            return

        api_query_url = make_idigbio_api_url("/v2/search/media", params)
        yield f"\n\n[View {record_count} matching media records]({api_query_url})"
        self.note(f"The API query matched {record_count} media records in iDigBio")

        self.set_results(Results(
            params=params,
            record_count=record_count,
            api_query_url=api_query_url
        ))


def _generate_records_search_parameters(agent: Agent, history: Conversation, request: str) -> dict:
    try:
        result = agent.client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            response_model=IDigBioMediaApiParameters,
            messages=history.render_to_openai(system_message=SYSTEM_PROMPT,
                                              request=request),
            max_retries=Retrying(stop=StopOnTerminalErrorOrMaxAttempts(3))
        )
    except InstructorRetryException as e:
        raise AgentGenerationException(e)

    params = result.model_dump(exclude_none=True, by_alias=True)
    return params


SYSTEM_PROMPT = f"""
You translate user requests into parameters for the iDigBio media search API.

Prefer to fill out the "mq" object. Only fill out the "rq" object if the user specifies occurrence-related criteria 
such as species taxonomy or locations.

If the user specifies a binomial scientific name, try to break it up into its genus and specific epithet. However, 
if the user specifies that they want to search for an exact scientific name, use the "scientificname" field. If the 
user places something in quotes, use the full text that is quoted, do not break it up.
"""
