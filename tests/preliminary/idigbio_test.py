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
