import instructor
import openai
from dotenv import load_dotenv
from instructor import Instructor, AsyncInstructor
from instructor.exceptions import InstructorRetryException
from openai import OpenAI
from tenacity import RetryCallState
from tenacity.stop import stop_base

load_dotenv()  # Load API key and patch the instructor client


class AI:
    openai: OpenAI
    client: Instructor | AsyncInstructor

    def __init__(self):
        self.openai = openai.OpenAI()
        self.client = instructor.from_openai(self.openai)


def _is_error_terminal(error: dict):
    return error.get("ctx", {}).get("terminal", False)


class AIGenerationException(Exception):
    def __init__(self, e: InstructorRetryException):
        messages = []
        terminal = False

        for error in e.args[0].errors():
            if _is_error_terminal(error):
                messages.append(f"Error: {error['msg']}")
                terminal = True

        if not terminal:
            messages.append(f"Error: AI failed to generate valid search parameters after {e.n_attempts} attempts.")

        self.message = "\n\n".join(messages)


class StopOnTerminalErrorOrMaxAttempts(stop_base):
    """Stop when a bad value is encountered."""

    def __init__(self, max_attempts: int):
        self.max_attempts = max_attempts

    def __call__(self, retry_state: RetryCallState) -> bool:
        for e in retry_state.outcome.exception().errors():
            if _is_error_terminal(e):
                return True

        return retry_state.attempt_number >= self.max_attempts
