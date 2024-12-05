import json
from typing import Iterable

import pytest
from pydantic.v1.utils import deep_update

from app import create_app
from chat.conversation import Conversation
from chat.messages import Message


@pytest.fixture(params=[({"config_overrides": None},)])
def app(request):
    test_config = {
        "CHAT": {
            "SHOW_PROCESSING_MESSAGES": True,
            "SAFE_MODE": False,
        },
    }

    if "config_overrides" in request.param:
        test_config = deep_update(test_config, request.param["config_overrides"])

    app = create_app(config_dict=test_config)
    app.testing = True

    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c


def chat(client, message) -> list[dict]:
    wrapped_response: Iterable[bytes] = client.post('/chat', json={
        "type": "user_text_message",
        "value": message
    }).response

    return parse_response_stream(wrapped_response)


def parse_response_stream(response) -> list[dict]:
    if isinstance(response, str):
        text = response
    else:
        text = "".join([m.decode("utf-8") for m in response])

    text = text.replace("\n", "\\n")
    return json.loads(text)


def make_convo(*messages: Message) -> Conversation:
    return Conversation([m.freeze() for m in messages])
