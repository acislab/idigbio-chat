import pytest

from chat_test_util import app, client, chat
from matchers import string_must_contain


@pytest.mark.parametrize("app", [{"config_overrides": {"CHAT": {"SAFE_MODE": True}}}], indirect=True)
def test_robo_check(app, client):
    messages = chat(client, "ping")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert "please confirm you are a real person" in messages[0]["value"]


@pytest.mark.parametrize("app", [{"config_overrides": {"CHAT": {"SAFE_MODE": True}}}], indirect=True)
def test_not_a_robot(app, client):
    messages = chat(client, "I am not a robot")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert not ("please confirm you are a real person" in messages[0]["value"])


@pytest.mark.parametrize("app", [{"config_overrides": {"CHAT": {"SAFE_MODE": False}}}], indirect=True)
def test_skip_robo_check(app, client):
    messages = chat(client, "ping")

    assert len(messages) >= 1
    assert messages[0]["type"] == "ai_text_message"
    assert not ("please confirm you are a real person" in messages[0]["value"])


def test_ping(client):
    messages = chat(client, "ping")

    assert len(messages) >= 1
    assert messages[0]["type"] == "ai_text_message"
    assert messages[0]["value"] == "pong"


@pytest.mark.parametrize("app", [{"config_overrides": {"CHAT": {"SAFE_MODE": True}}}], indirect=True)
def test_remember_robo_check(app, client):
    chat(client, "not a robot")
    chat(client, "clear")
    messages = chat(client, "ping")

    assert len(messages) >= 1
    assert messages[0]["value"] == "pong"


def test_echo(client):
    """Make the LLM say something predictable so we can check if its response is correctly transmitted."""
    messages = chat(client, "Repeat after me: Toast.")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert messages[0]["value"] == "Toast."


def test_describe_self(client):
    messages = chat(client, "What can you do?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_help(client):
    messages = chat(client, "help")

    assert len(messages) == 1
    assert messages[0]["value"].startswith("This is a prototype")


def test_simple_idigbio_search(client):
    messages = chat(client, "Find records for genus Carex")

    assert len(messages) == 2

    assert messages[0]["type"] == "ai_processing_message"
    content = messages[0]["value"]["content"]
    assert "```json" in content
    assert "https://search.idigbio.org/v2/search/records" in content

    assert messages[1]["type"] == "ai_text_message"


def test_simple_idigbio_map(client):
    messages = chat(client, "Show a map of genus Carex")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert "Carex" in messages[0]["value"]["content"]

    assert messages[1] == {
        "type": "ai_map_message",
        'value': {
            'rq': {'genus': 'Carex'}
        }
    }


def test_map_for_no_records(client):
    messages = chat(client, "Show a map of genus Jabberwock")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert "Jabberwock" in messages[0]["value"]["content"]

    assert messages[1]["type"] == "ai_text_message"


def test_expert_opinion(client):
    """"""
    messages = chat(client, "What color are polar bears? Please be brief.")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_conversation_history(client):
    """"""
    chat(client, "My name is Ruth.")
    messages = chat(client, "What is my name?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert "Ruth" in messages[0]["value"]


def test_conversation_history_map_query(client):
    """"""
    chat(client, "I want to talk about genus Carex")
    messages = chat(client, "Show a map")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1] == {
        "type": "ai_map_message",
        'value': {
            'rq': {'genus': 'Carex'}
        }
    }


def test_conversation_history_search_query(client):
    """"""
    chat(client, "I want to talk about genus Carex")
    messages = chat(client, "Find records")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1]["type"] == "ai_text_message"
    assert "Carex" in messages[1]["value"]


def test_follow_up_question_for_search_query(client):
    chat(client, "How many records for Ursus arctos are there")
    messages = chat(client, "What URL did you use to call the iDigBio API?")

    last_message = messages[-1]["value"]
    url = "https://search.idigbio.org/v2/summary/"
    assert string_must_contain(last_message, url, "Ursus arctos")


def test_count_records(client):
    messages = chat(client, "How many records for genus Carex?")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[0]["value"]["summary"] == "Searching iDigBio..."

    content = messages[0]["value"]["content"]
    assert '"genus": "Carex"' in content

    assert messages[1]["type"] == "ai_text_message"
    assert len(messages[1]["value"].splitlines()) == 1


def test_break_down_record_counts(client):
    messages = chat(client, "What 10 species have the most records in the United States?")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[0]["value"]["summary"] == "Searching iDigBio..."
    assert messages[1]["type"] == "ai_text_message"


def test_composite_request(client):
    messages = chat(client, "How many records of Ursus arctos are there in iDigBio and where are they on a map?")

    assert len(messages) == 4
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1]["type"] == "ai_text_message"
    assert messages[2]["type"] == "ai_processing_message"
    assert messages[3]["type"] == "ai_map_message"


def test_complex_search(client):
    messages = chat(client, "Find records for Rattus rattus in the US, Mexico, Canada, and Taiwan")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1]["type"] == "ai_text_message"


def test_search_by_date(client):
    messages = chat(client, "Find records between 1999 and 2020")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[0]["value"]["summary"] == "Searching iDigBio..."
    assert messages[1]["type"] == "ai_text_message"


def test_media_search(client):
    messages = chat(client, "Find media for genus Carex")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    content = messages[0]["value"]["content"]
    assert "https://search.idigbio.org/v2/search/media" in content


@pytest.mark.skip(reason="Not implemented")
def test_recommend_spelling_fix_with_no_matches():
    """
    Given a misspelled taxon name with zero matching records in iDigBio, respond with one or more recommendations
    e.g. "Did you mean X?"
    """
    # Trigger if zero matches in iDigBio?
    # Check GlobalNames parser to see if it's a valid name?
    # Check for synonyms?


@pytest.mark.skip(reason="Not implemented")
def test_recommend_spelling_fix_with_some_matches():
    """
    Given a misspelled taxon name with zero matching records in iDigBio, respond with one or more recommendations
    e.g. "Did you mean X?"
    """


@pytest.mark.skip(reason="Not implemented")
def test_records_field_lookup():
    """
    Tell the user which field to use in their search.
    """
    messages = chat(
        "I want to use iDigBio's records API. What fields will return location information for collection events?")
    assert False


@pytest.mark.skip(reason="Not implemented")
def test_explain_difference_between_data_and_index_fields():
    """
    Tell the user which field to use in their search.
    """
    messages = chat(
        "I want to use iDigBio's records API. What fields will return location information for collection events?")
    assert False
