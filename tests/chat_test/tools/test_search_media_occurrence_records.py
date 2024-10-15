from datetime import datetime

from chat.messages import UserMessage
from chat.processes.idigbio_media_search import IDigBioMediaSearch
from chat.tools.search_media_records import SearchMediaRecords
from chat_test.chat_test_util import make_history
from nlp.agent import Agent


def test_call():
    history = make_history(UserMessage("Find media for genus Ursus"))
    tool = SearchMediaRecords()
    messages = [m for m in tool.call(Agent(), history)]
    assert len(messages) == 2


def test_search_this_year():
    history = make_history(UserMessage("Find media created this year"))
    search = IDigBioMediaSearch(Agent(), history)

    year = str(datetime.now().year)

    assert "rq" in search.results.params
    assert "datemodified" in search.results.params["rq"]
    assert str(search.results.params["rq"]["datemodified"]["gte"]) == f"{year}-01-01"
    assert str(search.results.params["rq"]["datemodified"]["lte"]) == f"{year}-12-31"


def test_geopoint_exception():
    history = make_history(UserMessage("Find media for Ursus arctos with latitude=-100 and longitude=200"))
    search = IDigBioMediaSearch(Agent(), history)
    summary = search.summarize()
    assert summary == ('Error: Error: Invalid latitude value: -100.0 is not in range [-90, +90]\n'
                       '\n'
                       'Error: Error: Invalid latitude value: 200.0 is not in range [-180, +180]')
