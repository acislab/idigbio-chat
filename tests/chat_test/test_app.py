import pytest

import app
from chat_test_util import chat
from matchers import string_must_contain

app.chat_config["SHOW_PROCESSING_MESSAGES"] = True
app.chat_config["SAFE_MODE"] = False


def test_robo_check():
    app.chat_config["SAFE_MODE"] = True
    messages = chat("Hi!")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert "please confirm you are a real person" in messages[0]["value"]


def test_not_a_robot():
    app.chat_config["SAFE_MODE"] = True
    messages = chat("I am not a robot")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert not ("please confirm you are a real person" in messages[0]["value"])


def test_skip_robo_check():
    app.chat_config["SAFE_MODE"] = False
    messages = chat("Hi!")

    assert len(messages) >= 1
    assert messages[0]["type"] == "ai_text_message"
    assert not ("please confirm you are a real person" in messages[0]["value"])


def test_remember_robo_check():
    app.chat_config["SAFE_MODE"] = True
    chat("not a robot")
    chat("clear")
    messages = chat("hi")

    assert len(messages) >= 1
    assert not ("please confirm you are a real person" in messages[0]["value"])


def test_echo():
    """Make the LLM say something predictable so we can check if its response is correctly transmitted."""
    messages = chat("Repeat after me: Toast.")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert messages[0]["value"] == "Toast."


def test_describe_self():
    messages = chat("What can you do?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_off_topic():
    messages = chat("How's the weather?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_help():
    messages = chat("help")

    assert len(messages) == 1
    assert messages[0]["value"].startswith("This is a prototype")


def test_keep_users_list():
    users = app.redis.lrange("users", 0, -1)
    assert len(users) == 0

    chat("clear")

    users = app.redis.lrange("users", 0, -1)
    assert len(users) == 1


def test_simple_idigbio_search():
    messages = chat("Find records for genus Carex")

    assert len(messages) == 2

    assert messages[0]["type"] == "ai_processing_message"
    content = messages[0]["value"]["content"]
    assert "```json" in content
    assert "https://search.idigbio.org/v2/search/records" in content

    assert messages[1]["type"] == "ai_text_message"


def test_simple_idigbio_map():
    messages = chat("Show a map of genus Carex")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert "Carex" in messages[0]["value"]["content"]

    assert messages[1] == {
        "type": "ai_map_message",
        'value': {
            'rq': {'genus': 'Carex'}
        }
    }


def test_map_for_no_records():
    messages = chat("Show a map of genus Jabberwock")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert "Jabberwock" in messages[0]["value"]["content"]

    assert messages[1]["type"] == "ai_text_message"


def test_expert_opinion():
    """"""
    messages = chat("What color are polar bears? Please be brief.")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_conversation_history():
    """"""
    chat("My name is Ruth.")
    messages = chat("What is my name?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"
    assert "Ruth" in messages[0]["value"]


def test_conversation_history_map_query():
    """"""
    chat("I want to talk about genus Carex")
    messages = chat("Show a map")

    assert len(messages) == 3
    assert messages[0] == {
        'type': 'ai_processing_message',
        'value': {'summary': 'Searching for records...',
                  'content': {'rq': {'genus': 'Carex'}}}
    }
    assert messages[1]["value"].startswith("Here is")
    assert messages[2] == {
        "type": "ai_map_message",
        'value': {
            'rq': {'genus': 'Carex'}
        }
    }


def test_conversation_history_search_query():
    """"""
    chat("I want to talk about genus Carex")
    messages = chat("Find records")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1]["type"] == "ai_text_message"
    assert "Carex" in messages[1]["value"]


def test_follow_up_question_for_search_query():
    chat("How many records for Ursus arctos are there")
    messages = chat("What URL did you use to call the iDigBio API?")

    last_message = messages[-1]["value"]
    url = "https://search.idigbio.org/v2/summary/"
    assert string_must_contain(last_message, url, "Ursus arctos")


def test_count_records():
    messages = chat("How many records for genus Carex?")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[0]["value"]["summary"] == "Searching for records..."

    content = messages[0]["value"]["content"]
    assert '"genus": "Carex"' in content

    assert messages[1]["type"] == "ai_text_message"
    assert len(messages[1]["value"].splitlines()) == 1


def test_break_down_record_counts():
    messages = chat("What 10 species have the most records in the United States?")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[0]["value"]["summary"] == "Searching for records..."
    assert messages[1]["type"] == "ai_text_message"


def test_composite_request():
    messages = chat("How many records of Ursus arctos are there in iDigBio and where are they on a map?")

    assert len(messages) == 4
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1]["type"] == "ai_text_message"
    assert messages[2]["type"] == "ai_processing_message"
    assert messages[3]["type"] == "ai_map_message"


def test_complex_search():
    messages = chat("Find records for Rattus rattus in the US, Mexico, Canada, and Taiwan")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[1]["type"] == "ai_text_message"


def test_search_by_date():
    messages = chat("Find records between 1999 and 2020")

    assert len(messages) == 2
    assert messages[0]["type"] == "ai_processing_message"
    assert messages[0]["value"]["summary"] == "Searching for records..."
    assert messages[1]["type"] == "ai_text_message"


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
