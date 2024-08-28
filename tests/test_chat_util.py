from chat.chat_util import stream_value_as_text, stream_response_as_text, json_to_markdown
from chat.conversation import UserMessage, AiChatMessage, AiProcessingMessage


def test_stream_response_as_text():
    def weather_forecast():
        yield UserMessage("What's the weather tomorrow?")
        yield AiProcessingMessage("Fetching the weather...", "Hurricane")
        yield AiChatMessage("You don't wanna know")

    text = "".join(stream_response_as_text(weather_forecast()))

    assert text == """[{"type":"user_text_message","value":"What\'s the weather tomorrow?"},""" \
                   """{"type":"ai_processing_message","value":{"summary":"Fetching the weather...",""" \
                   """"content":"Hurricane"}},{"type":"ai_text_message","value":"You don\'t wanna know"}]"""


def test_stream_dict_as_text():
    d = {
        "type": "hotdog",
        "value": {
            "dog": "Ball Park Frank",
            "condiment": "relish"
        }
    }

    text = "".join(stream_value_as_text(d))

    assert text == """{"type":hotdog,"value":{"dog":Ball Park Frank,"condiment":relish}}"""


def test_stream_another_stream_as_text():
    def stream_ketchup():
        for c in "ketchup":
            yield c

    d = {
        "type": "hotdog",
        "value": {
            "dog": "Ball Park Frank",
            "condiment": stream_ketchup()
        }
    }

    text = "".join(stream_value_as_text(d))

    assert text == """{"type":hotdog,"value":{"dog":Ball Park Frank,"condiment":ketchup}}"""


def test_json_to_markdown():
    md = json_to_markdown({
        "rq": {
            "family": "Ursidae",
            "country": "Taiwan"
        },
        "limit": 10
    })

    assert md == """\
```json
{
    "rq": {
        "family": "Ursidae",
        "country": "Taiwan"
    },
    "limit": 10
}
```
"""
