from chat.conversation import AiMapMessage
from chat.stream_util import StreamedContent


def test_streamed_string_from_string():
    ss = StreamedContent("Just another string")
    ss.get()  # Empty the stream
    assert ss.get() == "Just another string"


def test_streamed_string_from_stream():
    ss = StreamedContent(iter("Just another string"))
    ss.get()  # Empty the stream
    assert ss.get() == "Just another string"
