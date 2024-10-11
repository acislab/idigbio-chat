import chat.api
from chat.conversation import Conversation
from chat.messages import UserMessage, AiChatMessage
from chat_test.chat_test_util import make_history
from nlp.agent import Agent


def test__break_down_message_into_smaller_requests():
    user_message = ("How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them "
                    "on a map.")
    conv = make_history(UserMessage(user_message))
    requests = chat.api._break_down_message_into_smaller_requests(Agent(), conv, user_message)

    assert len(requests) == 2

    assert "records" in requests[0]
    assert "polar bears" in requests[0]
    assert "Florida" in requests[0]
    assert "Orville Redenbacher" in requests[0]

    assert "show" in requests[1]
    assert "polar bears" in requests[1]
    assert "Florida" in requests[1]
    assert "Orville Redenbacher" in requests[1]
    assert "map" in requests[1]


def test_dont_break_up_complex_request():
    user_message = "Find records for Rattus rattus in the US, Mexico, Canada, and Taiwan"
    conv = make_history(UserMessage(user_message))
    requests = chat.api._break_down_message_into_smaller_requests(Agent(), conv, user_message)
    assert len(requests) == 1


def test_break_down_requests_with_history():
    conv = make_history(
        UserMessage(
            "How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them on a "
            "map."),
        AiChatMessage("Here are the records and here they are on a map."),
        UserMessage("How many of those records are in Alaska?")
    )

    requests = chat.api._break_down_message_into_smaller_requests(Agent(), conv, conv.render_to_openai()[-1]["content"])

    assert len(requests) == 1

    assert "records" in requests[0]
    assert "polar bears" in requests[0]
    assert "Alaska" in requests[0]
    assert "Orville Redenbacher" in requests[0]


def test_repeat_request_with_follow_up_information():
    conv = make_history(
        UserMessage("Please send the results to me by email."),
        AiChatMessage("Sure! Please tell me what email address to send them to."),
        UserMessage("orville.redenbacher@yahoo.com")
    )

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
