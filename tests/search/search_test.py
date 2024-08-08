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


def test_quote_some_jibber_jabber():
    """"""
    response = client.post("/search/generate_rq", json={
        "input": "species \"do not change this!\" in North America"
    })

    assert response.json == {
        "input": "species \"do not change this!\" in North America",
        "rq": {
            "scientificname": "do not change this!",
            "continent": "North America"
        },
        "result": "success",
        "message": ""
    }


def test_value_exists():
    """"""
    response = client.post("/search/generate_rq", json={
        "input": "Records with locality information"
    })

    assert response.json == {
        "input": "Records with locality information",
        "rq": {
            "locality": {
                "type": "exists"
            }
        },
        "result": "success",
        "message": ""
    }


def test_records_with_images():
    """"""
    response = client.post("/search/generate_rq", json={
        "input": "Records with images"
    })

    assert response.json == {
        "input": "Records with images",
        "rq": {
            "hasImage": "true"
        },
        "result": "success",
        "message": ""
    }


def test_update_input():
    """"""
    response = client.post("/search/update_input", json={
        "input": "Ursus arctos in North America",
        "rq": {
            "genus": "Ursus",
            "specificepithet": "arctos",
            "continent": "Australia"
        }
    })

    assert response.json == {
        "input": "Ursus arctos in Australia",
        "rq": {
            "genus": "Ursus",
            "specificepithet": "arctos",
            "continent": "Australia"
        },
        "result": "success",
        "message": ""
    }


def test_update_with_original_format():
    response = client.post("/search/update_input", json={
        "input": "genus: Ursus\nspecificepithet: arctos\ncountry: Canada\nprovince: Alberta",
        "rq": {
            "genus": "Ursus",
            "specificepithet": "arctos",
            "country": "Canada",
            "province": "Quebec"
        }
    })

    assert response.json == {
        "input": "genus: Ursus\nspecificepithet: arctos\ncountry: Canada\nprovince: Quebec",
        "rq": {
            "genus": "Ursus",
            "specificepithet": "arctos",
            "country": "Canada",
            "province": "Quebec"
        },
        "result": "success",
        "message": ""
    }
