from chat.content_streams import StreamedString


def test_streamed_string_from_string():
    ss = StreamedString(iter("Just another string"))
    ss.get()  # Empty the stream
    assert ss.get() == "Just another string"


def test_streamed_string_from_stream():
    ss = StreamedString(iter("Just another string"))
    ss.get()  # Empty the stream
    assert ss.get() == "Just another string"
