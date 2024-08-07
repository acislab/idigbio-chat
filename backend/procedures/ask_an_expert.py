from procedures.procedure import Procedure, all_procedures
from chat.agent import Agent
from chat.types import Conversation
from tools.expert_opinion import ask_llm_for_expert_opinion


class AskAnExpert(Procedure):
    schema = {
        "name": "ask_an_expert",
        "description": "If none of the other tools satisfy the user's request, ask an expert for help."
    }

    def call(self, agent: Agent, conversation: Conversation):
        """
        Asks the LLM to answer the user's prompt directly.
        """
        return ask_llm_for_expert_opinion(agent, conversation)


all_procedures.append(AskAnExpert())
