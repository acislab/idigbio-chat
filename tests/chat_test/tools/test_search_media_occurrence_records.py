from datetime import datetime

from chat.messages import UserMessage
from chat.processes.idigbio_media_search import IDigBioMediaSearch
from chat.tools.search_media_records import SearchMediaRecords
from chat_test.chat_test_util import make_history
from nlp.ai import AI
from test_util import clean, assert_string_matches_template


def test_call():
    history = make_history(UserMessage("Find media"))
    tool = SearchMediaRecords()
    messages = [m for m in tool.call(AI(), history)]
    assert len(messages) == 2


def test_notes():
    ref_summary = """
Generated search parameters:
```json
"mq": {}
```

Sending a POST request to the iDigBio media API at https://search.idigbio.org/v2/search/media

Response code: 200 OK

The API query matched {word} media records in iDigBio
"""
    history = make_history(UserMessage("Find media"))
    search = IDigBioMediaSearch(AI(), history)
    summary = search.describe()
    assert_string_matches_template(summary, ref_summary)


def test_mq_and_rq():
    history = make_history(UserMessage("Find media that have a specimen for species Ursus arctos"))
    search = IDigBioMediaSearch(AI(), history)

    assert clean(search.results.params) == {
        'mq': {
            'hasSpecimen': True
        },
        'rq': {
            'genus': 'Ursus',
            'specificepithet': 'arctos'
        }
    }


def test_find_by_uuid():
    history = make_history(UserMessage("Find media with uuid 8c73d3a5-aa07-478b-8bee-d74beb0c812f"))
    search = IDigBioMediaSearch(AI(), history)

    assert clean(search.results.params) == {
        "mq": {
            "uuid": "8c73d3a5-aa07-478b-8bee-d74beb0c812f"
        }
    }


def test_find_media_for_species():
    history = make_history(UserMessage("Find media for Ursus arctos"))
    search = IDigBioMediaSearch(AI(), history)

    assert clean(search.results.params) == {
        "rq": {
            "genus": "Ursus",
            "specificepithet": "arctos"
        }
    }


def test_search_this_year():
    history = make_history(UserMessage("Find media created this year using the datemodified field"))
    search = IDigBioMediaSearch(AI(), history)

    year = str(datetime.now().year)

    assert "mq" in search.results.params
    assert "datemodified" in search.results.params["mq"]
    assert str(search.results.params["mq"]["datemodified"]["gte"]) == f"{year}-01-01"
    assert str(search.results.params["mq"]["datemodified"]["lte"]) == f"{year}-12-31"


def test_geopoint_exception():
    history = make_history(UserMessage("Find media for Ursus arctos with latitude=-100 and longitude=200"))
    search = IDigBioMediaSearch(AI(), history)
    summary = search.describe()
    assert summary == ('Error: Error: Invalid latitude value: -100.0 is not in range [-90, +90]\n'
                       '\n'
                       'Error: Error: Invalid latitude value: 200.0 is not in range [-180, +180]')
