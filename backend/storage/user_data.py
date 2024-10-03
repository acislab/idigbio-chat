import json
from datetime import datetime
from uuid import uuid4

from flask.sessions import SessionMixin
from flask_session import Session
from redis import Redis

from chat.conversation import Conversation


class User:
    user_id: str
    history: Conversation

    def __init__(self, user_id: str, history: Conversation):
        self.user_id = user_id
        self.history = history


class UserData:

    def __init__(self, session: Session | SessionMixin, redis: Redis, config: dict):
        self.session = session
        self.redis = redis
        self.config = config

    def get_user_history_ptr(self, user_id: str):
        return user_id + "_history"

    def get_stored_user_history(self, user_id: str) -> Conversation:
        history_ptr = self.get_user_history_ptr(user_id)
        history = self.redis.lrange(history_ptr, 0, -1)

        def record(message):
            self.redis.rpush(history_ptr, json.dumps(message))

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
        self.redis.hset(user_id, "join_date", str(datetime.now().isoformat()))

        history = self.get_stored_user_history(user_id)
        return User(user_id, history)
