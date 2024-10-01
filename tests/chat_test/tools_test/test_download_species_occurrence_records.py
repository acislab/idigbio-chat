from chat.conversation import stream_response_as_text, Conversation
from chat.tools import download_species_occurrence_records
from chat.tools.download_species_occurrence_records import DownloadSpeciesOccurrenceRecords
from chat_test.chat_test_util import parse_response_stream
from nlp.agent import Agent


def test_good_call():
    download_species_occurrence_records.live = False

    agent = Agent()
    tool = DownloadSpeciesOccurrenceRecords()
    response = tool.call(agent, Conversation(), "Send records for Crangonyx floridanus to orville@pop.corn")

    messages = parse_response_stream("".join(stream_response_as_text(response)))

    assert "Response code: 200 (success)" in messages[0]["value"]["content"]


def test_missing_email():
    download_species_occurrence_records.live = False

    agent = Agent()
    tool = DownloadSpeciesOccurrenceRecords()
    response = tool.call(agent, Conversation(), "Send records for Crangonyx floridanus to orville")

    messages = parse_response_stream("".join(stream_response_as_text(response)))

    # TODO: chatbot should ask user for their email address
    assert False
