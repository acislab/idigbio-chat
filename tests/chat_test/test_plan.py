from chat.conversation import UserMessage
from chat.api import create_plan

from nlp.ai import AI
from test_util import make_history


def test_plan_get_records():
    user_request = "Find bears in Nebraska"
    plan = create_plan(
        ai=AI(),
        history=make_history(user_request),
        request=user_request
    )

    assert plan == "search_species_occurrence_records"


def test_plan_call_expert():
    user_request = "What color are bears?"
    plan = create_plan(
        ai=AI(),
        history=make_history(UserMessage(user_request)),
        request=user_request
    )

    assert plan == "ask_an_expert"
