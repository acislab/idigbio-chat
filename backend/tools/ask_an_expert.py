from chat.conversation import Conversation, AiMessage
from nlp.agent import Agent
from tools.tool import Tool


class AskAnExpert(Tool):
    schema = {
        "name": "ask_an_expert",
        "description": "If none of the other tools satisfy the user's request, ask an expert for help."
    }

    def call(self, agent: Agent, request: str, conversation=Conversation([]), state=None):
        """
        Asks the LLM to answer the user's prompt directly.
        """
        return ask_llm_for_expert_opinion(agent, conversation)


def ask_llm_for_expert_opinion(agent: Agent, conversation: Conversation):
    """
    Asks the LLM to answer the user's prompt directly.
    """
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        messages=conversation.render_to_openai("You are a biodiversity expert.")
    )

    return AiMessage(result.choices[0].message.content)
