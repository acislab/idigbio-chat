from typing import Iterator

from chat.chat_util import stream_openai
from chat.conversation import Conversation, AiChatMessage, Message
from chat.tools.tool import Tool
from nlp.agent import Agent


class Converse(Tool):
    schema = {
        "name": "converse",
        "description": "If the user is not requesting information or is requesting information that you cannot "
                       "provide, address their request in a friendly manner."
    }
    verbal_return_type = "a friendly conversational response"

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        yield _ask_llm_for_a_friendly_response(agent, history, request)


CONVERSATIONAL_PROMPT = """
You are a friendly artificial intelligence assistant that makes use of biodiversity information aggregated by 
iDigBio. You do not provide scientific data or knowledge directly, but call on biodiversity experts to help the user 
as needed. Keep your responses brief but friendly. If the user is requesting scientific information, apologize and 
admit that you do not know how to answer their query.
"""


def _ask_llm_for_a_friendly_response(agent: Agent, conversation: Conversation, request: str):
    """
    Asks the LLM to continue the conversation without providing scientific data.
    """
    result = agent.openai.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        stream=True,
        messages=conversation.render_to_openai(system_message=CONVERSATIONAL_PROMPT, request=request)
    )

    return AiChatMessage(stream_openai(result))
