from collections.abc import Iterator

from openai import OpenAI

from chat.conversation import Conversation, UserMessage, ErrorMessage, Message, AiMessage
from chat.plan import create_plan
from chat.tools.tool import all_tools
from nlp.agent import Agent

tool_lookup = {t.schema["name"]: t for t in all_tools}


def chat(agent: Agent, history: Conversation, user_message: str) -> Iterator[Message]:
    history.append(UserMessage(user_message))

    plan = create_plan(agent, history)
    tool_name = plan

    match tool_name:
        case "search_species_occurrence_records":
            yield present_results(agent, history, "a list of records")
        case "map_species_occurrences":
            yield present_results(agent, history, "a map species occurrences")
        case "ask_an_expert":
            yield present_results(agent, history, "a quote from Wikipedia")

    if tool_name in tool_name:
        response = tool_lookup[tool_name]().call(
            agent=agent,
            request=user_message,
            conversation=history,
            state={}
        )
    else:
        response = [ErrorMessage(f"Tried to use undefined tool \"{tool_name}\"")]

    history.append(response)

    for message in response:
        yield message


PRESENT_RESULTS_PROMPT = """
You are an assistant who announces what information is about to be provided to the user. You do not provide the 
information itself. You not know anything. You do not answer questions directly. Start all of your responses with 
\"Here is\" and end them with a colon. For example, \"Here is {0}:\""

The user is about to be shown {0}.
"""

client = OpenAI()


def stream_openai(response):
    for chunk in response:
        yield chunk.choices[0].delta.content


def present_results(agent, history, type_of_results):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=history.render_to_openai(PRESENT_RESULTS_PROMPT.format(type_of_results)),
        stream=True,
    )

    return AiMessage(stream_openai(response))
