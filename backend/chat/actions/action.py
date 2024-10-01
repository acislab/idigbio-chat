from chat.conversation import Conversation, Message, AiProcessingMessage
from chat.stream_util import StreamedString
from nlp.agent import Agent


class Action:
    process_summary: str
    __results: dict
    __content: StreamedString
    __notes: list[str] = []

    def __init__(self, agent: Agent, history=Conversation([]), request: str = None):
        self.__content = StreamedString(self.__run__(agent, history, request))

    @property
    def results(self):
        self.__content.get()
        return self.__results

    def set_results(self, results):
        self.__results = results

    def note(self, text: str):
        self.__notes += [text.strip()]
        return text

    def __run__(self, agent: Agent, history=Conversation([]), request: str = None) -> StreamedString:
        pass

    def summarize(self) -> str:
        return "\n\n".join(self.__notes)

    def make_message(self) -> Message:
        def think():
            yield self.summarize()

        return AiProcessingMessage(self.process_summary, self.__content, StreamedString(think()))
