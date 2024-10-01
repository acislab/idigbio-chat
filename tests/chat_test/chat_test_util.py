import json
from typing import Iterable

from app import app

app.testing = True
client = app.test_client()


def chat(message) -> list[dict]:
    wrapped_response: Iterable[bytes] = client.post('/chat', json={
        "type": "user_text_message",
        "value": message
    }).response

    return parse_response_stream(wrapped_response)


def parse_response_stream(response) -> dict:
    if isinstance(response, str):
        text = response
    else:
        text = "".join([m.decode("utf-8") for m in response])

    text = text.replace("\n", "\\n")
    return json.loads(text)
