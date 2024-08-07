from chat.procedures.procedure import Procedure, all_procedures
from chat.agent import Agent
from chat.types import Conversation
from tools.search_idigbio import ask_llm_to_generate_search_query


class SearchSpeciesOccurrenceRecords(Procedure):
    """
    Responds with links to call the iDigBio Records API and to the iDigBio Search Portal.
    """
    schema = {
        "name": "search_species_occurrence_records",
        "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                       "geographic distribution."
    }

    def call(self, agent: Agent, conversation: Conversation):
        return ask_llm_to_generate_search_query(agent, conversation)


all_procedures.append(SearchSpeciesOccurrenceRecords())
