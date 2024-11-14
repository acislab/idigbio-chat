import json
from datetime import datetime
from uuid import uuid4, UUID
from typing import Optional

from flask import request
from flask.sessions import SessionMixin
from flask_session import Session
from redis import Redis
from keycloak import KeycloakOpenID

from chat.conversation import Conversation
from chat.messages import ColdMessage

from storage.database import DatabaseEngine


class User:
    user_id: str
    history: Conversation

    def __init__(self, user_id: str, history: Conversation):
        self.user_id = user_id
        self.history = history


def get_user_hash_id(user_id: str):
    return f"user_{user_id}"


def get_user_history_ptr(user_id: str):
    conv_id = user_id  # Placeholder until we ID conversations
    return f"history_{user_id}_{conv_id}"


class UserData:

    def __init__(self, session: Session | SessionMixin, redis: Redis, config: dict, kc: KeycloakOpenID,
                 db: DatabaseEngine):
        self.session = session
        self.redis = redis
        self.config = config
        self.kc = kc
        self.db = db

    def get_temp_user_history(self, user_id: str) -> Conversation:
        if self.session.get('user'):
            return Conversation(None, None)
        else:
            history_ptr = get_user_history_ptr(user_id)
            raw_history = self.redis.lrange(history_ptr, 0, -1)

            def record(message: ColdMessage, conversation_id: Optional[UUID]):
                self.redis.rpush(history_ptr, message.stringify())

            history = [ColdMessage(json.loads(message)) for message in raw_history]
            return Conversation(history, record)

    def clear_temp_user_history(self, user_id: str):
        history_ptr = get_user_history_ptr(user_id)
        self.redis.delete(history_ptr)

    def temp_user_exists(self, user_id: str):
        user_hash = get_user_hash_id(self.session["id"])
        return self.redis.exists(user_hash)

    def get_temp_user(self) -> User | None:
        if "id" not in self.session or not self.temp_user_exists(self.session["id"]):
            if self.config["SAFE_MODE"]:
                return None
            else:
                return self.make_temp_user()

        user_id = self.session["id"]
        history = self.get_temp_user_history(user_id)
        return User(user_id, history)

    def make_temp_user(self) -> User:
        user_id = str(uuid4())
        self.session.permanent = True
        self.session["id"] = user_id

        self.redis.rpush("users", user_id)
        self.redis.hset(get_user_hash_id(user_id), "join_date", str(datetime.now().isoformat()))

        history = self.get_temp_user_history(user_id)
        return User(user_id, history)

    def login(self, auth_code):
        token = self.kc.token(
            grant_type='authorization_code',
            code=auth_code,
            redirect_uri=request.root_url,
        )
        userinfo = self.kc.userinfo(token['access_token'])

        self.session['user'] = userinfo
        self.session['token'] = token

        if self.db.user_exists(userinfo['sub']):
            return userinfo
        else:
            self.db.insert_user(userinfo)

        return userinfo

    def logout(self):
        self.session.clear()
        self.session.pop('session_key', None)
        self.kc.logout(refresh_token=None)

# class UserEntity(db.Model):
#     __tablename__ = 'user_entity'
#     id = db.Column(db.String, primary_key=True)  # Assuming it's a string ID from Keycloak
#     # ... other columns you might have

#     # Add relationship to see conversations easily
#     conversations = db.relationship('Conversation', backref='user', lazy=True)

# class Conversation(db.Model):
#     __tablename__ = 'conversations'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.String, db.ForeignKey('user_entity.id'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     # Add relationship to see messages easily
#     messages = db.relationship('Message', backref='conversation', lazy=True)

# class Message(db.Model):
#     __tablename__ = 'messages'

#     id = db.Column(db.Integer, primary_key=True)
#     conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
