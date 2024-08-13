from nlp.agent import Agent
from chat.tools.search_species_occurrence_records import SearchSpeciesOccurrenceRecords


def test_call():
    agent = Agent()
    tool = SearchSpeciesOccurrenceRecords()
    response = tool.call(agent, "Find records for genus Ursus")
    assert response["rq"] == {
        "genus": "Ursus"
    }
