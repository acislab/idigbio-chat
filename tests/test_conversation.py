from chat.conversation import Conversation, AiProcessingMessage, stream_response_as_text, get_record_count, \
    stream_record_counts_as_markdown_table, generate_records_summary_parameters
from idigbio_util import url_encode_params
from nlp.agent import Agent


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


def test_get_record_counts_as_markdown_table():
    params = {
        "rq": {
            "country": "Canada",
            "family": "Ursidae"
        },
        "top_fields": "genus",
        "count": 5
    }

    url_params = url_encode_params(params)
    total, counts = get_record_count(f"https://search.idigbio.org/v2/summary/top/records?{url_params}")

    table = "".join(stream_record_counts_as_markdown_table(counts))

    assert table.startswith("|")
    assert len(table.splitlines()) == 5
    assert table.endswith("\n")


def test_generate_records_summary_parameters():
    params = generate_records_summary_parameters(Agent(), Conversation(),
                                                 "What are 3 species of Ursidae in Costa Rica?")

    assert "count" in params
    assert params["count"] == 3
    assert params["rq"] == {
        "family": "Ursidae",
        "country": "Costa Rica"
    }
