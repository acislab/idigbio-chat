from chat_test.messages import UserMessage
from chat_test.conversation import Conversation


def test_append():
    conv = Conversation()
    conv.append(UserMessage("Good morning"))
    assert conv.conversation[0].read_all() == {
        'role_and_content': [{'content': 'Good morning', 'role': 'user'}],
        'show_user': True,
        'tool_name': '',
        'type': 'user_text_message',
        'type_and_value': {'type': 'user_text_message', 'value': 'Good morning'}
    }


def test_render_to_openai():
    conv = Conversation()
    conv.append(UserMessage("Good morning"))
    assert conv.render_to_openai("This is the system message", "Good morning")[:2] == [
        {'role': 'system', 'content': 'This is the system message'},
        {'role': 'user', 'content': 'Good morning'}
    ]
