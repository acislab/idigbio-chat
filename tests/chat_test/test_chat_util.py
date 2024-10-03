from chat.utils.json import stream_as_json, make_pretty_json_string
from chat.messages import UserMessage, AiChatMessage, AiProcessingMessage, stream_messages


def test_stream_response_as_json():
    def weather_forecast():
        yield UserMessage("What's the weather tomorrow?")
        yield AiProcessingMessage("Fetching the weather...", "Hurricane")
        yield AiChatMessage("You don't wanna know")

    text = "".join(stream_messages(weather_forecast()))

    assert text == """[{"type":"user_text_message","value":"What\'s the weather tomorrow?"},""" \
                   """{"type":"ai_processing_message","value":{"summary":"Fetching the weather...",""" \
                   """"content":"Hurricane"}},{"type":"ai_text_message","value":"You don\'t wanna know"}]"""


def test_stream_dict_as_json():
    d = {
        "type": "hotdog",
        "value": {
            "dog": "Ball Park Frank",
            "condiments": ["relish", "onions"],
            "count": 1,
            "cook": {
                "name": "Chip",
                "age": 10
            }
        }
    }

    text = "".join(stream_as_json(d))

    assert text == ('{"type":"hotdog","value":{"dog":"Ball Park Frank","condiments":["relish","onions"],"count":1,'
                    '"cook":{"name":"Chip","age":10}}}')


def test_stream_another_stream_as_json():
    d = {
        "type": "hotdog",
        "value": {
            "dog": "Ball Park Frank",
            "condiment": (c for c in "ketchup")
        }
    }

    text = "".join(stream_as_json(d))

    assert text == """{"type":"hotdog","value":{"dog":"Ball Park Frank","condiment":"ketchup"}}"""


def test_stream_containing_quotes():
    pass


def test_stream_containing_newlines():
    pass


def test_json_to_markdown():
    md = make_pretty_json_string({
        "rq": {
            "family": "Ursidae",
            "country": "Taiwan"
        },
        "limit": 10
    })

    assert md == """\
{
    "rq": {
        "family": "Ursidae",
        "country": "Taiwan"
    },
    "limit": 10
}\
"""
