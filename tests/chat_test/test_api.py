import chat.api
from chat.messages import UserMessage, AiChatMessage
from chat_test.chat_test_util import make_history
from matchers import string_must_contain
from nlp.ai import AI


def test__break_down_message_into_smaller_requests():
    user_message = ("How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them "
                    "on a map.")
    conv = make_history(UserMessage(user_message))
    requests = chat.api._break_down_message_into_smaller_requests(AI(), conv, user_message)

    assert len(requests) == 2
    assert string_must_contain(requests[0], "records", "polar bears", "Florida", "Orville Redenbacher")
    assert string_must_contain(requests[1], "show", "polar bears", "Florida", "Orville Redenbacher", "map")


def test_dont_break_up_complex_request():
    user_message = "Find records for Rattus rattus in the US, Mexico, Canada, and Taiwan"
    conv = make_history(UserMessage(user_message))
    requests = chat.api._break_down_message_into_smaller_requests(AI(), conv, user_message)
    assert len(requests) == 1


def test_break_down_requests_with_history():
    conv = make_history(
        UserMessage(
            "How many records are there for polar bears in Florida collected by Orville Redenbacher? Show them on a "
            "map."),
        AiChatMessage("Here are the records and here they are on a map."),
        UserMessage("How many of those records are in Alaska?")
    )

    requests = chat.api._break_down_message_into_smaller_requests(AI(), conv, conv.render_to_openai()[-1]["content"])

    assert len(requests) == 1
    assert string_must_contain(requests[0], "records", "polar bears", "Alaska", "Orville Redenbacher")


def test_repeat_request_with_follow_up_information():
    conv = make_history(
        UserMessage("Please send the results to me by email."),
        AiChatMessage("Sure! Please tell me what email address to send them to."),
        UserMessage("orville.redenbacher@yahoo.com")
    )

    requests = chat.api._break_down_message_into_smaller_requests(AI(), conv, conv.render_to_openai()[-1]["content"])

    assert len(requests) == 1
    assert string_must_contain(requests[0], "send the results", "orville.redenbacher@yahoo.com")


def test_dont_repeat_request_with_follow_up_questions():
    conv = make_history(
        UserMessage("How many bear records are there in iDigBio"),
        AiChatMessage("There are 100 bear records"),
        UserMessage("What URL did you use to call the iDigBio API to find records?")
    )

    requests = chat.api._break_down_message_into_smaller_requests(AI(), conv, conv.render_to_openai()[-1]["content"])

    assert string_must_contain(requests[0], "URL", "iDigBio API", "find records", "horse")


def test_off_topic():
    request = "How's the weather?"
    conv = make_history(UserMessage(request))
    tool = chat.api.create_plan(AI(), conv, request)

    assert tool == "converse"


def test_media_search():
    request = "Find media for genus Carex"
    conv = make_history(UserMessage(request))
    tool = chat.api.create_plan(AI(), conv, request)

    assert tool == "search_media_records"
