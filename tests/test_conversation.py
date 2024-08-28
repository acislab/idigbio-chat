from chat.conversation import Conversation, AiProcessingMessage, stream_response_as_text


def test_render_for_openai():
    conv = Conversation([
        {"type": "ai_text_message", "value": "a1"},
        {"type": "user_text_message", "value": "u1"}
    ])

    texts = conv.render_to_openai("This is the system message")

    assert texts == [
        {'role': 'system', 'content': 'This is the system message'},
        {'role': 'assistant', 'content': 'a1'},
        {'role': 'user', 'content': 'u1'}
    ]


def test_render_error():
    conv = Conversation([
        {"type": "something made up", "value": "uh oh"},
    ])

    texts = conv.render_to_openai("This is the system message")

    assert texts == [
        {'role': 'system', 'content': 'This is the system message'},
        {'role': 'error',
         'content': "Failed to parse message data: {'type': 'something made up', 'value': 'uh oh'}\n'something made "
                    "up' is not a valid MessageType", }
    ]


def test_ai_processing_message_with_dict():
    def response():
        yield AiProcessingMessage(summary="Test summary", content={
            "one": 1,
            "condiments": {
                "below": "ketchup",
                "above": "mustard"
            }
        })

    as_text = "".join(stream_response_as_text(response()))

    assert as_text == """\
[{"type":"ai_processing_message","value":"```json
{
    \\"summary\\": \\"Test summary\\",
    \\"content\\": {
        \\"one\\": 1,
        \\"condiments\\": {
            \\"below\\": \\"ketchup\\",
            \\"above\\": \\"mustard\\"
        }
    }
}
```
"}]\
"""
