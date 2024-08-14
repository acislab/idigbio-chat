from typing import Iterator

from chat.conversation import Conversation, AiMessage, Message
from chat.tools.tool import Tool
from nlp.agent import Agent


class Converse(Tool):
    schema = {
        "name": "converse",
        "description": "If the user is not requesting information or is requesting information that you cannot "
                       "provide, address their request in a friendly manner."
    }
    verbal_return_type = "a friendly conversational response"

    def call(self, agent: Agent, request: str, history=Conversation([]), state=None) -> Iterator[Message]:
        yield _ask_llm_for_a_friendly_response(agent, history)


def _ask_llm_for_a_friendly_response(agent: Agent, conversation: Conversation):
    """
    Asks the LLM to continue the conversation without providing scientific data.
    """
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        messages=conversation.render_to_openai(
            "You are a friendly artificial intelligence assistant that makes use of biodiversity information "
            "aggregated by iDigBio. You do not provide scientific data or knowledge directly, but call on "
            "biodiversity experts to help the user as needed. Keep your responses brief but friendly. If the user is "
            "requesting scientific information, apologize and admit that you do not know how to answer their query.")
    )

    return AiMessage(result.choices[0].message.content)
