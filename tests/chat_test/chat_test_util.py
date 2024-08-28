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

    text = "".join([m.decode("utf-8") for m in wrapped_response])
    text = text.replace("\n", "\\n")

    messages = json.loads(text)
    return messages
