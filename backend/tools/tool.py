import glob
import importlib
from os.path import dirname, basename, isfile, join

from chat.conversation import Conversation
from nlp.agent import Agent

# Automatically populated with all children of Tool in the "tools" package
all_tools = []


class Tool:
    """
    Implements all the logic needed to generate an appropriate response to a user query.
    """
    schema: dict

    def call(self, agent: Agent, request: str, conversation=Conversation([]), state=None):
        pass


def __gather_tools():
    modules = glob.glob(join(dirname(__file__), "*.py"))
    tool_modules = [f".{basename(f)[:-3]}" for f in modules if
                    isfile(f) and not (f.endswith('/__init__.py') or f.endswith("/tool.py"))]

    for mod in tool_modules:
        importlib.import_module(mod, package="tools")

    all_tools.extend(Tool.__subclasses__())
