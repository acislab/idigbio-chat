import app
from .chat_test_util import chat

app.SHOW_PROCESSING_MESSAGES = True


def test_be_friendly():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("Hi!")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_describe_self():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("What can you do?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_off_topic():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("How's the weather?")

    assert len(messages) == 1
    assert messages[0]["type"] == "ai_text_message"


def test_help():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("help")

    assert len(messages) == 1
    assert messages[0] == {
        "type": "ai_text_message",
        "value": "I have access to the following tools..."
    }


def test_simple_idigbio_search():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("Find records for genus Carex")

    assert len(messages) == 4
    assert messages[0] == {
        'type': 'ai_processing_message',
        'value': {'summary': 'Searching for records...',
                  'content': {'rq': {'genus': 'Carex'}}}
    }
    assert messages[1]["value"].startswith("Here is")
    assert messages[2] == {'type': 'ai_text_message',
                           'value': '[iDigBio portal search](https://beta-portal.idigbio.org/portal/search?rq={'
                                    '"genus":"Carex"})'}
    assert messages[3] == {'type': 'ai_text_message',
                           'value': '[iDigBio API search](https://search.idigbio.org/v2/search/records?rq={'
                                    '"genus":"Carex"})'}


def test_simple_idigbio_map():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("Show a map of genus Carex")

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


def test_expert_opinion():
    """"""
    messages = chat("What color are polar bears? Please be brief.")

    assert len(messages) == 2
    assert messages[0]["value"].startswith("Here is")

    m = messages[1]
    assert m["type"] == "ai_text_message"
    assert "polar bears" in m["value"].lower()
    assert "white" in m["value"].lower()


def test_conversation_history():
    """"""
    chat("What color are polar bears? Please be brief.")
    messages = chat("Where do they live? Please be brief.")

    assert len(messages) == 2
    assert messages[0]["value"].startswith("Here is")

    m = messages[1]
    assert "polar bear" in m["value"].lower()
    assert "arctic" in m["value"].lower()


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

    assert len(messages) == 4
    assert messages[0] == {
        'type': 'ai_processing_message',
        'value': {'summary': 'Searching for records...',
                  'content': {'rq': {'genus': 'Carex'}}}
    }
    assert messages[1]["value"].startswith("Here is")
    assert messages[2] == {'type': 'ai_text_message',
                           'value': '[iDigBio portal search](https://beta-portal.idigbio.org/portal/search?rq={'
                                    '"genus":"Carex"})'}
    assert messages[3] == {'type': 'ai_text_message',
                           'value': '[iDigBio API search](https://search.idigbio.org/v2/search/records?rq={'
                                    '"genus":"Carex"})'}


def test_count_records():
    messages = chat("How many records for genus Carex?")

    assert len(messages) == 3
    assert messages[0] == {
        'type': 'ai_processing_message',
        'value': {'summary': 'Searching for records...',
                  'content': {'rq': {'genus': 'Carex'}}}
    }
    assert messages[1]["value"].startswith("Here is")
    assert messages[2]["type"] == "ai_text_message"
    assert messages[2]["value"].startswith("Record count")


def test_recommend_spelling_fix_with_no_matches():
    """
    Given a misspelled taxon name with zero matching records in iDigBio, respond with one or more recommendations
    e.g. "Did you mean X?"
    """
    # Trigger if zero matches in iDigBio?
    # Check GlobalNames parser to see if it's a valid name?
    # Check for synonyms?


def test_recommend_spelling_fix_with_some_matches():
    """
    Given a misspelled taxon name with zero matching records in iDigBio, respond with one or more recommendations
    e.g. "Did you mean X?"
    """


def test_records_field_lookup():
    """
    Tell the user which field to use in their search.
    """
    messages = chat(
        "I want to use iDigBio's records API. What fields will return location information for collection events?")
    assert False


def test_explain_difference_between_data_and_index_fields():
    """
    Tell the user which field to use in their search.
    """
    messages = chat(
        "I want to use iDigBio's records API. What fields will return location information for collection events?")
    assert False