from chat.conversation import Conversation


def test_render_for_openai():
    conv = Conversation([
        {"type": "ai_text_message", "value": "a1"},
        {"type": "user_text_message", "value": "u1"}
    ])

    texts = conv.render("This is the system message")

    assert texts == [
        {'role': 'system', 'content': 'This is the system message'},
        {'role': 'assistant', 'content': 'a1'},
        {'role': 'user', 'content': 'u1'}
    ]


def test_render_error():
    conv = Conversation([
        {"type": "something made up", "value": "uh oh"},
    ])

    texts = conv.render("This is the system message")

    assert texts == [
        {'role': 'system', 'content': 'This is the system message'},
        {'role': 'error',
         'content': "Failed to parse message data: {'type': 'something made up', 'value': 'uh oh'}\n'something made "
                    "up' is not a valid MessageType", }
    ]
