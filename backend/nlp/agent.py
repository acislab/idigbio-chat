import instructor
import openai
from dotenv import load_dotenv

load_dotenv()  # Load API key and patch the instructor client


class Agent:
    def __init__(self):
        self.client = instructor.from_openai(openai.OpenAI())
