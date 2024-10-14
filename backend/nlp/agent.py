import instructor
import openai
from dotenv import load_dotenv
from instructor import Instructor, AsyncInstructor
from openai import OpenAI

load_dotenv()  # Load API key and patch the instructor client


class Agent:
    openai: OpenAI
    client: Instructor | AsyncInstructor

    def __init__(self):
        self.openai = openai.OpenAI()
        self.client = instructor.from_openai(self.openai)
