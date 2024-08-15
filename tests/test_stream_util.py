from chat.conversation import AiMapMessage
from chat.stream_util import StreamedString


def test_streamed_string_from_string():
    ss = StreamedString("Just another string")
    ss.get_string()  # Empty the stream
    assert ss.get_string() == "Just another string"


def test_streamed_string_from_stream():
    ss = StreamedString(iter("Just another string"))
    ss.get_string()  # Empty the stream
    assert ss.get_string() == "Just another string"
