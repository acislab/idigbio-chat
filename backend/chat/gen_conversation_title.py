from typing import Iterator

from chat.conversation import Conversation
from chat.messages import AiChatMessage, Message
from chat.tools.tool import Tool
from chat.utils.json import stream_openai
from nlp.ai import AI

DESCRIPTION = """
This tool is used to generate a relevant title for a conversation. 
"""

PROMPT = """
You are a conversation title generation agent. Your role is to analyze conversation histories and generate clear, 
descriptive titles that will help users find their conversations later.
The title is of type character varying(36).
Key Responsibilities:

Generate concise titles (3-8 words) that capture the main topic or purpose of the conversation
Focus on the primary subject matter rather than tangential discussions
Prioritize specificity over generic descriptions
Use natural, readable language rather than technical or system-oriented terms
Include relevant proper nouns, technical terms, or specific topics when they are central to the discussion

Guidelines for Title Generation:

Identify the core topic by analyzing:

The initial query or request
Recurring themes throughout the conversation
The most substantive or detailed exchanges
Any explicit task or goal being discussed


Format titles to be:

Capitalized appropriately (first letter of major words)
Free of unnecessary punctuation
Written in plain language
Descriptive but not overly long


Prioritize including:

Specific technologies, tools, or platforms discussed
Types of problems being solved
Particular skills or domains involved
Project names or specific tasks
Key concepts or methodologies


Avoid:

Generic titles like "General Discussion" or "Quick Question"
System-oriented language like "Conversation About" or "Discussion Regarding"
Including usernames or personal identifiers
Timestamps or dates unless specifically relevant
Emojis or special characters



Examples of Good Titles:

"PostgreSQL Database Optimization Tips"
"React Component Testing Strategy"
"Marketing Campaign Budget Analysis"
"Python Script for PDF Processing"
"Website Color Scheme Design"

Examples of Poor Titles:

"Chat from Tuesday"
"Discussion with Assistant"
"Technical Question"
"Help Needed"
"Various Topics"

Always ensure the title is something a user would recognize and associate with their conversation when scanning 
through a list of past chats. The title should immediately remind them of what was discussed and why the conversation 
was important.
Output Format:

Provide only the generated title
Do not include explanations or multiple options
Do not prefix with "Title:" or similar labels

Remember: Users will rely on these titles to find important conversations later, so accuracy and specificity are 
crucial. 
"""


class GenConversationTitle():
    name = 'gen_conversation_title'
    description = DESCRIPTION

    def call(self, ai: AI, conversation: Conversation, request: str, state: dict) -> Iterator[Message]:
        result = _ask_llm_to_generate_title(ai, request)
        yield result


def _ask_llm_to_generate_title(ai: AI, request: str):
    print('AI')
    print(ai)
    print(request)
    result = ai.openai.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=[
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": request
            }
        ]
    )
    return result.choices[0].message.content
