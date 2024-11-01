from datetime import datetime

from chat.messages import UserMessage
from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.tools.search_species_occurrence_records import SearchSpeciesOccurrenceRecords
from chat_test.chat_test_util import make_history
from nlp.ai import AI
from test_util import assert_string_matches_template


def test_call():
    tool = SearchSpeciesOccurrenceRecords()
    messages = [m for m in tool.call(AI(), make_history(UserMessage("Find records for genus Ursus")))]
    assert len(messages) == 2


def test_notes():
    ref_summary = """
Generated search parameters:
```json
"rq": {
    "mediarecords": {
        "type": "exists"
    }
}
```

Sending a POST request to the iDigBio records API at https://search.idigbio.org/v2/search/records

Response code: 200 OK

The API query matched {word} records in iDigBio using the URL https://search.idigbio.org/v2/search/records?rq={
"mediarecords":{"type":"exists"}}

The records can be viewed in the iDigBio portal at https://portal.idigbio.org/portal/search?rq={"mediarecords":{
"type":"exists"}}. The portal shows the records in an interactive list and plots them on a map. The raw records 
returned returned by the API can be found at https://search.idigbio.org/v2/search/records?rq={"mediarecords":{
"type":"exists"}}
"""
    history = make_history(UserMessage("Find media"))
    search = IDigBioRecordsSearch(AI(), history)
    summary = search.describe()
    assert_string_matches_template(summary, ref_summary)


def test_search_this_year():
    history = make_history(UserMessage("Find records created this year"))
    search = IDigBioRecordsSearch(AI(), history)

    year = str(datetime.now().year)

    assert "rq" in search.results.params
    assert "datemodified" in search.results.params["rq"]
    assert str(search.results.params["rq"]["datemodified"]["gte"]) == f"{year}-01-01"
    assert str(search.results.params["rq"]["datemodified"]["lte"]) == f"{year}-12-31"


def test_geopoint_exception():
    history = make_history(UserMessage("Generate a search query for Ursus arctos with latitude=-100 and longitude=200"))
    search = IDigBioRecordsSearch(AI(), history)
    summary = search.describe()
    assert summary == ('Error: Error: Invalid latitude value: -100.0 is not in range [-90, +90]\n'
                       '\n'
                       'Error: Error: Invalid latitude value: 200.0 is not in range [-180, +180]')


def test_aliased_field_search():
    """
    The field "class" is a keyword in Python, so we have to use Pydantic's alias feature to serialize the field name
    as a string. Aliases must be enabled in Pydantic's "[obj].model_dump" method.
    """
    history = make_history(UserMessage("Find records of Aves"))
    search = IDigBioRecordsSearch(AI(), history)
    assert search.results.params["rq"] == {
        "class": "Aves"
    }


def test_existence_search():
    history = make_history(UserMessage("Records that specify a common name"))
    search = IDigBioRecordsSearch(AI(), history)

    assert search.results.params["rq"] == {
        "commonname": {
            "type": "exists"
        }
    }


def test_has_image():
    history = make_history(UserMessage("Records with no images"))
    search = IDigBioRecordsSearch(AI(), history)

    assert search.results.params["rq"] == {
        "hasImage": False
    }
