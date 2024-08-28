import chat.api
from chat.conversation import Conversation
from nlp.agent import Agent


def test__break_down_message_into_smaller_requests():
    agent = Agent()

    user_message = ("How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them "
                    "on a map.")
    conv = Conversation([
        {"type": "user_text_message",
         "value": user_message}
    ])

    requests = chat.api._break_down_message_into_smaller_requests(agent, conv, user_message)

    assert requests == [
        "how many records are there for polar bears in Florida collected by Orville Redenbacher",
        "show records for polar bears in Florida collected by Orville Redenbacher on a map"
    ]


def test_break_down_requests_with_history():
    agent = Agent()

    conv = Conversation([
        {"type": "user_text_message",
         "value": "How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them "
                  "on a map."},
        {"type": "ai_text_message",
         "value": "Here are the records and here they are on a map. How else can I help you?"},
        {"type": "user_text_message",
         "value": "How many of those records are in Alaska?"}
    ])

    requests = chat.api._break_down_message_into_smaller_requests(agent, conv, conv.render_to_openai()[-1]["content"])

    assert requests == [
        "how many records for polar bears collected by Orville Redenbacher are in Alaska"
    ]
