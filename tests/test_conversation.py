from chat.conversation import Conversation
from chat.messages import UserMessage


def test_append():
    conv = Conversation()
    conv.append(UserMessage("Good morning"))
    assert conv.history[0].read_all() == {
        "show_user": True,
        "tool_name": "",
        "type": "user_text_message",
        "openai_messages": [{"content": "Good morning", "role": "user"}],
        "frontend_messages": {"type": "user_text_message", "value": "Good morning"}
    }


def test_render_to_openai():
    conv = Conversation()
    conv.append(UserMessage("Good morning"))

    openai_messages = conv.render_to_openai("This is the system message", "Good morning")

    assert openai_messages[0]["role"] == "system"
    assert openai_messages[0]["content"].endswith("This is the system message")

    assert openai_messages[1] == {"role": "user", "content": "Good morning"}
