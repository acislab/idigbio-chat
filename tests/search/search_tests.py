from app import app

app.testing = True
client = app.test_client()


def test_simple_search():
    """"""
    response = client.post("/search/generate_rq", json={
        "input": "Ursus arctos in North America"
    })

    assert response.json == {
        "input": "Ursus arctos in North America",
        "rq": {
            "genus": "Ursus",
            "specificepithet": "arctos",
            "continent": "North America"
        },
        "result": "success",
        "message": ""
    }


def test_off_topic():
    """"""
    response = client.post("/search/generate_rq", json={
        "input": "What color are bears?"
    })

    assert response.json == {
        "input": "What color are bears?",
        "rq": {},
        "result": "error",
        "message": "Failed to understand user input"
    }


def test_exact_name_match():
    """"""
    response = client.post("/search/generate_rq", json={
        "input": "Only Ursus arctos (Smith 1900) in North America"
    })

    assert response.json == {
        "input": "Only Ursus arctos (Smith 1900) in North America",
        "rq": {
            "scientificname": "Ursus arctos (Smith 1900)",
            "continent": "North America"
        },
        "result": "success",
        "message": ""
    }
