from typing import Iterator

from chat.conversation import Conversation
from chat.messages import AiChatMessage, Message
from chat.tools.tool import Tool
from chat.utils.json import stream_openai
from nlp.ai import AI

DESCRIPTION = """\
If the user is not requesting information or is requesting information that you cannot provide, this function will 
address their request in a friendly manner.
"""


class Converse(Tool):
    name = "converse"
    description = DESCRIPTION
    output = None

    def call(self, ai: AI, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        yield _ask_llm_for_a_friendly_response(ai, history, request)


CONVERSATIONAL_PROMPT = """
You are a friendly AI assistant that makes use of biodiversity information aggregated by iDigBio. You do not provide 
scientific data or knowledge directly, but relay information found in online biodiversity resources that may help 
answer user requests. Keep your responses brief but friendly. If the user wants to know something that is already 
contained described in the ongoing conversation - especially factual information - apologize and admit that you do 
not know how to answer their request.
"""


def _ask_llm_for_a_friendly_response(ai: AI, conversation: Conversation, request: str):
    """
    Asks the LLM to continue the conversation without providing scientific data.
    """
    result = ai.openai.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        stream=True,
        messages=conversation.render_to_openai(system_message=CONVERSATIONAL_PROMPT, request=request)
    )

    return AiChatMessage(stream_openai(result))
