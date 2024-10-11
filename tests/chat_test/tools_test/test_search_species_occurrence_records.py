from datetime import datetime

from chat.messages import UserMessage
from chat.processes.idigbio_records_search import IDigBioRecordsSearch
from chat.tools.search_species_occurrence_records import SearchSpeciesOccurrenceRecords
from chat_test.chat_test_util import make_history
from nlp.agent import Agent


def test_call():
    agent = Agent()
    tool = SearchSpeciesOccurrenceRecords()
    response = tool.call(agent, "Find records for genus Ursus")
    assert response["rq"] == {
        "genus": "Ursus"
    }


def test_search_this_year():
    history = make_history(UserMessage("Find records created this year"))
    search = IDigBioRecordsSearch(Agent(), history)

    year = str(datetime.now().year)

    assert "rq" in search.results.params
    assert "datemodified" in search.results.params["rq"]
    assert str(search.results.params["rq"]["datemodified"]["gte"]) == f"{year}-01-01"
    assert str(search.results.params["rq"]["datemodified"]["lte"]) == f"{year}-12-31"
