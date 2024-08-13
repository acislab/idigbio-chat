from app import app

app.testing = True
client = app.test_client()


def chat(user_message) -> list[dict]:
    wrapped_response = client.post('/chat', json={
        "message": user_message
    }).response

    messages = [m for m in wrapped_response]
    # noinspection PyTypeChecker
    return messages


def test_simple_idigbio_search():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    messages = chat("Find records for genus Carex")

    assert messages == [
        {
            "type": "ai_message",
            'value': {
                'rq': {'genus': 'Carex'}
            }
        }
    ]


def test_expert_opinion():
    """"""
    messages = chat("What color are polar bears? Please be brief.")

    assert len(messages) == 1

    m = messages[0]
    assert m["type"] == "ai_message"
    assert "polar bears" in m["value"].lower()
    assert "white" in m["value"].lower()


def test_conversation():
    """"""
    chat("What color are polar bears? Please be brief.")
    messages = chat("Where do they live? Please be brief.")

    assert len(messages) == 1

    m = messages[0]
    assert "polar bear" in m["value"].lower()
    assert "arctic" in m["value"].lower()


def test_recommend_spelling_fix_with_no_matches():
    """
    Given a misspelled taxon name with zero matching records in iDigBio, respond with one or more recommendations
    e.g. "Did you mean X?"
    """


def test_recommend_spelling_fix_with_some_matches():
    """
    Given a misspelled taxon name with zero matching records in iDigBio, respond with one or more recommendations
    e.g. "Did you mean X?"
    """


def test_generate_a_checklist():
    """
    Query ElasticSearch for unique species at a given location
    """
