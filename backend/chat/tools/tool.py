import glob
import importlib
from os.path import dirname, basename, isfile, join
from typing import Iterator

from chat.conversation import Conversation, Message
from nlp.agent import Agent

# Automatically populated with all children of Tool in the "tools" package
all_tools = []


class Tool:
    """
    Implements all the logic needed to generate an appropriate response to a user query.
    """
    schema: dict
    verbal_return_type: str

    def call(self, agent: Agent, conversation=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        """
        :param agent: An interface for using LLMs.
        :param conversation: Stores all user- and AI-generated messages.
        :param request: The user request currently being addressed. Note that complicated user messages are broken
        down into multiple requests.
        :param state: TODO: A place to keep persistent data (not implemented)
        :return:
        """
        pass


def __gather_tools():
    modules = glob.glob(join(dirname(__file__), "*.py"))
    tool_modules = [f".{basename(f)[:-3]}" for f in modules if
                    isfile(f) and not (f.endswith('/__init__.py') or f.endswith("/tool.py"))]

    for mod in tool_modules:
        importlib.import_module(mod, package=__package__)

    all_tools.extend(Tool.__subclasses__())
