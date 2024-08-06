import instructor
import openai
from dotenv import load_dotenv

from idigbio_records_api_schema import LLMQueryOutput

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI())


def ask_llm_for_expert_opinion(prompt: str):
    result = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        response_model=None,
        messages=[
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return {
        "type": "expert",
        "data": {
            "source": "LLM",
            "text": result.choices[0].message.content
        }
    }
