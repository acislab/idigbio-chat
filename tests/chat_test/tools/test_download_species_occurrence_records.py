import pytest

from chat.conversation import Conversation
from chat.messages import stream_messages, UserMessage
from chat.processes.idigbio_records_download import IDigBioRecordsDownload
from chat.tools import download_species_occurrence_records
from chat.tools.download_species_occurrence_records import DownloadSpeciesOccurrenceRecords
from chat_test.chat_test_util import parse_response_stream, make_history
from nlp.ai import AI
from test_util import assert_string_matches_template


def test_good_call():
    download_species_occurrence_records.live = False

    ai = AI()
    tool = DownloadSpeciesOccurrenceRecords()
    response = tool.call(ai, Conversation(), "Send records for Crangonyx floridanus to orville@pop.corn")

    messages = parse_response_stream("".join(stream_messages(response)))

    assert "Response code: 200 OK" in messages[0]["value"]["content"]


def test_notes():
    download_species_occurrence_records.live = False
    ref_summary = """
Generated search parameters:
```json
"rq": {},
"email": "test@idigbio.org"
```

Sending a POST request to the iDigBio download API at https://search.idigbio.org/v2/download

Response code: 200 OK

Requested records download link to be sent to test@idigbio.org!

The records can be viewed in the iDigBio portal at https://portal.idigbio.org/portal/search?email="test@idigbio.org". 
The portal shows the records in an interactive list and plots them on a map. The raw records returned returned by the 
API can be found at https://search.idigbio.org/v2/search/records?email="test@idigbio.org". The user can resend the 
download request manually using https://search.idigbio.org/v2/download?email="test@idigbio.org".
"""
    history = make_history(UserMessage("Send everything to test@idigbio.org"))
    process = IDigBioRecordsDownload(AI(), history)
    summary = process.describe()
    assert_string_matches_template(summary, ref_summary)


@pytest.mark.skip(reason="Not implemented")
def test_missing_email():
    download_species_occurrence_records.live = False

    ai = AI()
    tool = DownloadSpeciesOccurrenceRecords()
    response = tool.call(ai, Conversation(), "Send records for Crangonyx floridanus to orville")

    messages = parse_response_stream("".join(stream_messages(response)))

    # TODO: chatbot should ask user for their email address
    assert False
