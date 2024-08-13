from chat.conversation import UserMessage
from chat.plan import create_plan
from nlp.agent import Agent
from test_util import test_conversation


def test_plan_get_records():
    user_message = "Find bears in Nebraska"
    plan = create_plan(
        agent=Agent(),
        conversation=test_conversation(user_message)
    )

    assert plan == "search_species_occurrence_records"


def test_plan_call_expert():
    query = "What color are bears?"
    plan = create_plan(
        agent=Agent(),
        conversation=test_conversation(UserMessage(query))
    )

    assert plan == "ask_an_expert"
