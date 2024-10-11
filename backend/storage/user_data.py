import json
from datetime import datetime
from uuid import uuid4

from flask.sessions import SessionMixin
from flask_session import Session
from redis import Redis

from chat.conversation import Conversation
from chat.messages import ColdMessage


class User:
    user_id: str
    history: Conversation

    def __init__(self, user_id: str, history: Conversation):
        self.user_id = user_id
        self.history = history


def get_user_hash_id(user_id: str):
    return f"user_{user_id}"


class UserData:

    def __init__(self, session: Session | SessionMixin, redis: Redis, config: dict):
        self.session = session
        self.redis = redis
        self.config = config

    def get_user_history_ptr(self, user_id: str):
        conv_id = user_id  # Placeholder until we ID conversations
        return f"history_{user_id}_{conv_id}"

    def get_stored_user_history(self, user_id: str) -> Conversation:
        history_ptr = self.get_user_history_ptr(user_id)
        raw_history = self.redis.lrange(history_ptr, 0, -1)

        def record(message: ColdMessage):
            self.redis.rpush(history_ptr, message.stringify())

        history = [ColdMessage(json.loads(message)) for message in raw_history]
        return Conversation(history, record)

    def clear_stored_user_history(self, user_id: str):
        history_ptr = self.get_user_history_ptr(user_id)
        self.redis.delete(history_ptr)

    def get_user(self) -> User | None:
        if "id" not in self.session or not self.redis.exists(self.session["id"]):
            if self.config["SAFE_MODE"]:
                return None
            else:
                return self.make_user()

        user_id = self.session["id"]
        history = self.get_stored_user_history(user_id)
        return User(user_id, history)

    def make_user(self) -> User:
        user_id = str(uuid4())
        self.session["id"] = user_id

        self.redis.rpush("users", user_id)
        self.redis.hset(get_user_hash_id(user_id), "join_date", str(datetime.now().isoformat()))

        history = self.get_stored_user_history(user_id)
        return User(user_id, history)
