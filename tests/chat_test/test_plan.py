from chat.conversation import UserMessage
from chat.api import create_plan

from nlp.ai import AI
from test_util import make_convo


def test_plan_get_records():
    user_request = "Find bears in Nebraska"
    plan = create_plan(ai=AI(), conversation=make_convo(user_request), request=user_request)

    assert plan == "search_species_occurrence_records"


def test_plan_call_expert():
    user_request = "What color are bears?"
    plan = create_plan(ai=AI(), conversation=, request=user_request)

    assert plan == "ask_an_expert"
