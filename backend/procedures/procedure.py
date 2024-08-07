from openai.types.chat import ChatCompletionMessageParam

from chat.agent import Agent

# Other scripts populate this list with instances of procedures
all_procedures = []


class Procedure:
    """
    Implements all the logic needed to generate an appropriate response to a user query.
    """
    schema: dict

    def call(self, agent: Agent, conversation: list[ChatCompletionMessageParam]):
        pass
