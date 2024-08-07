from chat.agent import Agent
from chat.types import Conversation


def ask_llm_for_expert_opinion(agent: Agent, conversation: Conversation):
    """
    Asks the LLM to answer the user's prompt directly.
    """
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        messages=conversation
    )

    return {
        "type": "expert",
        "data": {
            "source": "LLM",
            "text": result.choices[0].message.content
        }
    }
