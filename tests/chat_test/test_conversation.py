from chat.processes.idigbio_records_summary import _generate_records_summary_parameters, \
    _stream_record_counts_as_markdown_table, _query_summary_api
from chat.messages import AiProcessingMessage, AiChatMessage, UserMessage
from chat.messages import stream_messages
from chat.conversation import Conversation
from chat_test.chat_test_util import make_history
from idigbio_util import url_encode_params
from nlp.agent import Agent


def test_render_for_openai():
    conv = make_history(
        AiChatMessage("a1"),
        UserMessage("u1")
    )

    texts = conv.render_to_openai("This is the system message", system_header="(header) ")

    assert texts == [
        {'role': 'system', 'content': '(header) This is the system message'},
        {'role': 'assistant', 'content': 'a1'},
        {'role': 'user', 'content': 'u1'}
    ]


def test_render_for_openai_with_datetime():
    conv = make_history(AiChatMessage("a1"))
    texts = conv.render_to_openai("This is the system message")
    assert texts[0]["content"].startswith("Today's date is")


def test_ai_processing_message_with_dict():
    def response():
        yield AiProcessingMessage(summary="Test summary", content={
            "one": 1,
            "condiments": {
                "below": "ketchup",
                "above": "mustard"
            }
        })

    as_text = "".join(stream_messages(response()))

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
    total, counts = _query_summary_api(
        f"https://search.idigbio.org/v2/summary/top/records?{url_params}")

    table = "".join(_stream_record_counts_as_markdown_table(counts))

    assert table.startswith("|")
    assert len(table.splitlines()) == 5
    assert table.endswith("\n")


def test_generate_records_summary_parameters():
    params = _generate_records_summary_parameters(Agent(), Conversation(),
                                                  "What are 3 species of Ursidae in Costa Rica?")

    assert "count" in params
    assert params["count"] == 3
    assert params["rq"] == {
        "family": "Ursidae",
        "country": "Costa Rica"
    }
