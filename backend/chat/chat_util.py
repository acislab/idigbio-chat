from openai import OpenAI

from chat.conversation import AiChatMessage

PRESENT_RESULTS_PROMPT = """
You are an assistant who announces what information is about to be provided to the user. You do not provide the 
information itself. You not know anything. You do not answer questions directly. Start all of your responses with 
\"Here is\" and end them with a colon. For example, \"Here is {0}:\""

The user is about to be shown {0}.
"""

client = OpenAI()


def stream_openai(response):
    yield '"'
    for chunk in response:
        yield chunk.choices[0].delta.content
    yield '"'


def present_results(agent, history, type_of_results):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=history.render_to_openai(PRESENT_RESULTS_PROMPT.format(type_of_results)),
        stream=True,
    )

    return AiChatMessage(stream_openai(response))
