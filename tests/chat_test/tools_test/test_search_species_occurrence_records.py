from chat.tools.search_species_occurrence_records import SearchSpeciesOccurrenceRecords
from nlp.agent import Agent


def test_call():
    agent = Agent()
    tool = SearchSpeciesOccurrenceRecords()
    response = tool.call(agent, "Find records for genus Ursus")
    assert response["rq"] == {
        "genus": "Ursus"
    }
