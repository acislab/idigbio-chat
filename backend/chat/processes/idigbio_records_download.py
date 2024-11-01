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
from schema.idigbio.api import IDigBioRecordsApiParameters, IDigBioDownloadApiParameters

live = True


@dataclass
class Results(dict):
    params: dict
    download_api_url: str
    success: bool


class IDigBioRecordsDownload(Process):
    process_summary = "Creating iDigBio download request..."

    def __run__(self, ai: AI, history, request: str) -> StreamedString:
        try:
            params = _generate_records_download_parameters(ai, history, request)
        except AIGenerationException as e:
            yield self.note(e.message)
            return

        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```")

        download_api_url = make_idigbio_api_url("/v2/download")
        self.note(f"Sending a POST request to the iDigBio download API at {download_api_url}")

        portal_url = make_idigbio_portal_url(params)
        records_api_query_url = make_idigbio_api_url("/v2/search/records", params)
        download_api_query_url = make_idigbio_api_url("/v2/download", params)

        if live:
            response_code, success, _ = query_idigbio_api("/v2/download", params)
        else:
            response_code, success = "200 OK", True

        yield self.note(f"\n\nResponse code: {response_code}")
        yield f" | [Resend request]({download_api_query_url})"

        if success:
            self.note(f"Requested records download link to be sent to {params['email']}!")
        else:
            yield self.note(f"\n\nError! Something went wrong!")
            return

        self.note(
            f"The records can be viewed in the iDigBio portal at {portal_url}. The portal shows the records in an "
            f"interactive list and plots them on a map. The raw records returned returned by the API can be found at "
            f"{records_api_query_url}. The user can resend the download request manually using "
            f"{download_api_query_url}."
        )

        self.set_results(Results(
            params=params,
            download_api_url=download_api_query_url,
            success=success
        ))


def _generate_records_download_parameters(ai: AI, history: Conversation, request: str) -> dict:
    result = ai.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioDownloadApiParameters,
        messages=history.render_to_openai(system_message=search.functions.generate_rq.SYSTEM_PROMPT, request=request),
    )

    params = result.model_dump(exclude_none=True, by_alias=True)
    return params


def _generate_records_search_parameters(ai: AI, history: Conversation, request: str) -> dict:
    try:
        result = ai.client.chat.completions.create(
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
