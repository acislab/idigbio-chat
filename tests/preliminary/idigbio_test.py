import requests as rq


def test_get_countries():
    records = rq.post("https://search.idigbio.org/v2/search/records", json={
        "rq": {"scientificname": "acer saccharum"},
        "fields": ["country", "data.dwc:country"]
    }).json()

    raw_countries = {r["data"]["dwc:country"].lower() for r in records['items']}
    assert raw_countries == {"united states", "estados unidos de america"}

    indexed_countries = {r["indexTerms"]["country"].lower() for r in records['items']}
    assert indexed_countries == {"united states"}

    # But r["indexTerms"]["indexData"] doesn't exist?


def test_get_only_countries():
    records = rq.post("https://search.idigbio.org/v2/search/records", json={
        "rq": {"scientificname": "acer saccharum"},
    }).json()

    raw_countries = {r["data"]["dwc:country"].lower() for r in records['items']}
    assert raw_countries == {"united states", "estados unidos de america"}

    indexed_raw_countries = {r["indexTerms"]["indexData"]["dwc:country"].lower() for r in records['items']}
    assert indexed_raw_countries == {"united states"}

    indexed_countries = {r["indexTerms"]["country"].lower() for r in records['items']}
    assert indexed_countries == {"united states"}


def test_bad_post():
    response = rq.post("https://search.idigbio.org/v2/search/records", json={"rq": "crash!!"})

    assert response.json() == {
        'error': 'unable to parse parameter',
        'name': 'ParameterParseError',
        'parameter': 'rq',
        'statusCode': 400
    }


def _get_fields(data: dict, deep: bool):
    if type(data) is dict:
        for k, v in data.items():
            if type(v) is dict:
                if tuple(v.keys()) == ("type", "fieldName"):
                    yield v
                elif deep:
                    for f in _get_fields(v, True):
                        yield f


def get_fields(data: dict, deep=False) -> list[dict[str, str]]:
    return [f for f in _get_fields(data, deep)]


def test_get_fields():
    response = rq.get("https://search.idigbio.org/v2/meta/fields/records")

    data = response.json()
    top_level_fields = get_fields(data)
    aggs_fields = get_fields(data["aggs"], deep=True)
    data_fields = get_fields(data["data"], deep=True)
    indexData_fields = get_fields(data["indexData"], deep=True)
