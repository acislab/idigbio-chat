from typing import Iterator

from chat.conversation import Conversation
from chat.messages import Message, AiProcessingMessage
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI


class AskAnExpert(Tool):
    name = "ask_an_expert"
    description = "If none of the other tools satisfy the user's request, ask an expert for help."
    output = None

    def call(self, ai: AI, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        """
        Asks the LLM to answer the user's prompt directly.
        """

        result = (
            "Something went wrong. The system either failed to understand the user's request or is incapable of "
            "handling it.")
        yield AiProcessingMessage("Thinking...", result, show_user=False)
        yield present_results(ai, history, request, result + "\n\nPlease apologize.")
