import json
from typing import Iterable, Optional

import pytest
import sqlalchemy
from pydantic.v1.utils import deep_update

from app import create_app
from chat.conversation import Conversation
from chat.messages import Message
from storage.database import DatabaseEngine


@pytest.fixture(params=[({"config_overrides": None},)])
def app(request):
    test_config = {
        "SESSION_PERMANENT": True,
        "CHAT": {
            "SAFE_MODE": False,
            "SHOW_INTRO_MESSAGE": True,
        },
    }

    if "config_overrides" in request.param:
        test_config = deep_update(test_config, request.param["config_overrides"])

    engine = sqlalchemy.create_engine("sqlite://")
    db = DatabaseEngine(engine)

    app = create_app(config_dict=test_config, database=db)
    app.testing = True

    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c


def chat(client, message, conversation_id="7141b7e1-d5f6-40c1-b032-118aece4e708") -> list[dict]:
    wrapped_response: Iterable[bytes] = client.post('/chat', json={
        "type": "user_text_message",
        "value": message,
        "conversation_id": conversation_id
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
