import instructor
import openai
from dotenv import load_dotenv

load_dotenv()  # Load API key and patch the instructor client
client = instructor.from_openai(openai.OpenAI(base_url="http://localhost:8000/v1", api_key="ollama"))


def test_local_llm():
    prompt = "Find Ursus arctos occurrence records"
    out = client.chat.completions.create(
        model="hugging-quants/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4",
        temperature=0,
        response_model=None,
        max_tokens=100,
        messages=[
            {
                "role": "system",
                "content": "You call functions to find species occurrence records that may help answer users' "
                           "biodiversity-related queries. You do not answer queries yourself. If no other functions "
                           "match the user's query, call for help from an expert using the ask_an_expert function."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
    pass
