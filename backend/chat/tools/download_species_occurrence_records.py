from collections.abc import Iterator

from chat.plans import DataType
from chat.processes.idigbio_records_download import IDigBioRecordsDownload
from chat.conversation import Conversation
from chat.messages import Message
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI

live = True

DESCRIPTION = """\
Begins a search for species occurrence records using the iDigBio records API. Once the search is completed, 
the results are packaged as a DarwinCore Archive zip file and sent to a specified email address.
"""


class DownloadSpeciesOccurrenceRecords(Tool):
    name = "download_species_occurrence_records"
    description = DESCRIPTION
    output = DataType.species_occurrence_records_download_email

    def call(self, ai: AI, history: Conversation, request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioRecordsDownload(ai, history, request)
        yield search.make_message()

        if search.results.success:
            success_message = (
                "\n\nPlease inform the user that the download request was sent and they should receive an email when "
                "their download is ready."
            )
        else:
            success_message = "\n\nPlease inform the user that something went wrong with the download request."

        yield present_results(ai, history, request, search.describe() + success_message)
