from typing import Iterator

from chat.conversation import Conversation
from chat.messages import AiChatMessage, Message
from chat.tools.tool import Tool
from chat.utils.json import stream_openai
from nlp.agent import Agent


class Converse(Tool):
    schema = {
        "name": "converse",
        "description": "If the user is not requesting information or is requesting information that you cannot "
                       "provide, this function will address their request in a friendly manner."
    }

    def call(self, agent: Agent, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        yield _ask_llm_for_a_friendly_response(agent, history, request)


CONVERSATIONAL_PROMPT = """
You are a friendly AI assistant that makes use of biodiversity information aggregated by iDigBio. You do not provide 
scientific data or knowledge directly, but relay information found in online biodiversity resources that may help 
answer user requests. Keep your responses brief but friendly. If the user wants to know something that is already 
contained described in the ongoing conversation - especially factual information - apologize and admit that you do 
not know how to answer their request.
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
    

    return AiChatMessage("".join(filter(None, stream_openai(result))))

