from chat.content_streams import StreamedString
from chat.conversation import Conversation
from chat.messages import Message, AiProcessingMessage
from nlp.ai import AI


class Process:
    """
    A complex process that tools can run to interface with external APIs, analyze data, etc. The executed process and
    its results should be communicated to the user in an AiProcessingMessage.

    Attributes:
        process_summary (str): A short description of what the process is supposed to do
        results (dict): A set of structured outcomes of the process
    """
    process_summary: str
    results: dict

    def __init__(self, ai: AI, history: Conversation, request: str = None):
        self.__content: StreamedString = StreamedString(self.__run__(ai, history, request))
        self.__notes: list[str] = []
        self.__results: dict = dict()

    @property
    def results(self):
        self.__content.gobble()
        return self.__results

    def set_results(self, results):
        """
        Called by the process to store its results.
        """
        self.__results = results

    def note(self, text: str):
        """
        :param text: Leave a note for the chatbot to remember. This does not make the note visible to the user.
        :return:
        """
        self.__notes += [text.strip()]
        return text

    def __run__(self, ai: AI, history: Conversation, request: str) -> StreamedString:
        """
        Run the process, generating messages (via "yield" operators) and collecting notes along the way to help the
        LLM understand the steps and outputs of the process, including any warnings or errors encountered during
        execution.
        """
        pass

    def describe(self) -> str:
        """
        :return: Compiles the notes created while executing the process.
        """
        self.__content.gobble()
        return "\n\n".join(self.__notes)

    def make_message(self) -> Message:
        """
        :return: An AiProcessingMessage that describes the executed process and its outcomes.
        """

        def think():
            yield self.describe()

        return AiProcessingMessage(self.process_summary, self.__content, StreamedString(think()))
