from chat.content_streams import StreamedString
from chat.conversation import Conversation
from chat.messages import AiChatMessage
from chat.utils.json import stream_openai
from nlp.ai import AI

PRESENT_RESULTS_PROMPT = """
You are an assistant who relays information to the user. You not know anything. Only use what information has been 
provided to you as context to address the user's request. If some context information indirectly answers the user's 
question, try to cite that information. For example, if the user wants to know whether a species is present in a 
particular location, and if the context information shows that there are 1000 records of the species in that location, 
then mention the number of records instead of just saying "Yes". So, a good response might be "Yes, there are 1000 
records of the species in that location"

If the provided context information does help you answer to the user's request, apologize that you could not 
answer their request. Do not respond with any information that is not already available in the conversation or 
provided context.

Use the context information below:

{context}
"""


def present_results(ai: AI, conversation: Conversation, request: str, results: str | StreamedString) -> AiChatMessage:
    response = ai.openai.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=conversation.render_to_openai(PRESENT_RESULTS_PROMPT.format(request=request, context=results),
                                               request),
        stream=True,
    )
    print('PRESENT RESULTS FULL RESPOSNE:')
    full_response = ''
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content

    return AiChatMessage(full_response)
