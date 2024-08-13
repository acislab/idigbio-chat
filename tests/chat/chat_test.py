from app import app

app.testing = True
client = app.test_client()


def test_simple_idigbio_search():
    """Require the chatbot to infer that the user wants to search iDigBio, then build an appropriate API query"""
    response = client.post('/chat', json={
        "message": "Find records for genus Carex"
    }).json

    assert response == [
        {
            "type": "ai_message",
            'value': {
                'rq': {'genus': 'Carex'}
            }
        }
    ]


def test_expert_opinion():
    """"""
    response = client.post('/chat', json={
        "message": "What color are polar bears? Please be brief."
    }).json

    assert len(response) == 1

    r = response[0]
    assert r["type"] == "ai_message"
    assert "polar bears" in r["value"].lower()
    assert "white" in r["value"].lower()


def test_conversation():
    """"""
    client.post('/chat', json={
        "message": "What color are polar bears? Please be brief."
    })

    response = client.post('/chat', json={
        "message": "Where do they live? Please be brief."
    }).json

    assert len(response) == 1

    r = response[0]
    assert "polar bear" in r["value"].lower()
    assert "arctic" in r["value"].lower()


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
