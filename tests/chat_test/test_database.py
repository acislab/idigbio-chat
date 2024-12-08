import pytest
import sqlalchemy

from chat.messages import UserMessage, AiProcessingMessage, AiChatMessage
from storage.database import DatabaseEngine


@pytest.fixture
def db(request):
    # TODO: enable foreign key constraints with sqlite
    engine = sqlalchemy.create_engine("sqlite://")
    db = DatabaseEngine(engine)
    return db


def test_create_permanent_user(db: DatabaseEngine):
    user = {
        "id": "0fee2103-7467-47ee-a224-dc739a5eb619",
        "temp": False
    }

    assert not db.user_exists(user["id"])
    assert not db.temp_user_exists(user["id"])

    db.insert_user(user)

    assert db.user_exists(user["id"])
    assert not db.temp_user_exists(user["id"])


def test_create_temp_user(db: DatabaseEngine):
    user = {
        "id": "0fee2103-7467-47ee-a224-dc739a5eb619",
        "temp": True
    }

    assert not db.user_exists(user["id"])
    assert not db.temp_user_exists(user["id"])

    db.insert_user(user)

    assert not db.user_exists(user["id"])
    assert db.temp_user_exists(user["id"])


def test_conversation_tracking(db: DatabaseEngine):
    user_id = "0fee2103-7467-47ee-a224-dc739a5eb619"
    conv_id = "03cb9be7-993a-4625-b546-2ab2f63fcfc3"

    message = UserMessage("Hi!").freeze()
    message_id = message.read("message_id")

    db.insert_user({"id": user_id, "temp": False})
    db.create_conversation_history(conv_id, user_id, "A friendly chat")
    assert db.conversation_history_exists(conv_id)

    db.write_message_to_storage(message, conv_id)
    assert db.get_user_conversations(user_id) == [{
        "id": "03cb9be7-993a-4625-b546-2ab2f63fcfc3",
        "title": "A friendly chat"
    }]

    conv = db.get_conversation(conv_id)
    assert conv.history[0].read_all() == {
        "id": message_id,
        "type": "user_text_message",
        "tool_name": "",
        "openai_messages": [{
            "role": "user",
            "content": "Hi!"
        }],
        "frontend_messages": {
            "id": message_id,
            "type": "user_text_message",
            'value': "Hi!"
        }
    }


def test_frontend_conversation_messaages(db: DatabaseEngine):
    user_id = "0fee2103-7467-47ee-a224-dc739a5eb619"
    conv_id = "03cb9be7-993a-4625-b546-2ab2f63fcfc3"

    db.insert_user({"id": user_id, "temp": False})
    db.create_conversation_history(conv_id, user_id, "A friendly chat")

    message_ids = []
    for message in [
        UserMessage("Hi!"),
        AiChatMessage("01010111001")
    ]:
        message_ids.append(message.message_id)
        db.write_message_to_storage(message.freeze(), conv_id)

    assert list(db.stream_conversation_for_frontend(conv_id)) == [
        {"id": message_ids[0], "type": "user_text_message", "value": "Hi!"},
        {"id": message_ids[1], "type": "ai_text_message", "value": "01010111001"}
    ]
