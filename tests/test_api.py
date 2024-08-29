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

    assert len(requests) == 2

    assert "how many records" in requests[0]
    assert "polar bears" in requests[0]
    assert "Florida" in requests[0]
    assert "Orville Redenbacher" in requests[0]

    assert "show" in requests[1]
    assert "polar bears" in requests[1]
    assert "Florida" in requests[1]
    assert "Orville Redenbacher" in requests[1]
    assert "map" in requests[1]


def test_break_down_requests_with_history():
    conv = Conversation([
        {"type": "user_text_message",
         "value": "How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them "
                  "on a map."},
        {"type": "ai_text_message",
         "value": "Here are the records and here they are on a map. How else can I help you?"},
        {"type": "user_text_message",
         "value": "How many of those records are in Alaska?"}
    ])

    requests = chat.api._break_down_message_into_smaller_requests(Agent(), conv, conv.render_to_openai()[-1]["content"])

    assert len(requests) == 1

    assert "how many records" in requests[0]
    assert "polar bears" in requests[0]
    assert "Alaska" in requests[0]
    assert "Orville Redenbacher" in requests[0]


def test_repeat_request_with_follow_up_information():
    conv = Conversation([
        {"type": "user_text_message",
         "value": "Please send the results to me by email."},
        {"type": "ai_text_message",
         "value": "Sure! What is your email address?"},
        {"type": "user_text_message",
         "value": "orville.redenbacher@yahoo.com"}
    ])

    requests = chat.api._break_down_message_into_smaller_requests(Agent(), conv, conv.render_to_openai()[-1]["content"])

    assert len(requests) == 1
    assert "send the results" in requests[0]
    assert "orville.redenbacher@yahoo.com" in requests[0]


def test_dont_repeat_request_with_follow_up_questions():
    conv = Conversation([
        {"type": "user_text_message",
         "value": "How many bear records are there in iDigBio"},
        {"type": "ai_text_message",
         "value": "There are 100 bear records"},
        {"type": "user_text_message",
         "value": "What URL did you use to call the iDigBio API to find records?"}
    ])

    requests = chat.api._break_down_message_into_smaller_requests(Agent(), conv, conv.render_to_openai()[-1]["content"])

    assert requests == [
        "What URL did you use to call the iDigBio API to find records?"
    ]
