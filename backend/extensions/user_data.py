import json
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID

import flask
from flask import request, Flask, current_app
from keycloak import KeycloakOpenID
from redis import Redis

from chat.conversation import Conversation
from chat.messages import ColdMessage
from storage.database import DatabaseEngine


class User:
    user_id: str
    conversation: Conversation

    def __init__(self, user_id: str, conversation: Conversation):
        self.user_id = user_id
        self.conversation = conversation


def get_user_hash_id(user_id: str):
    return f"user_{user_id}"


def get_user_history_ptr(user_id: str):
    conv_id = user_id  # Placeholder until we ID conversations
    return f"history_{user_id}_{conv_id}"


class UserData:
    redis: Redis
    kc: KeycloakOpenID
    db: DatabaseEngine

    def init_app(self, app: Flask, redis: Redis, kc: KeycloakOpenID,
                 db: DatabaseEngine):
        self.redis = redis
        self.kc = kc
        self.db = db

    def get_temp_user_conversation_history(self, user_id: str) -> Conversation:
        if flask.session.get("user"):
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
        user_hash = get_user_hash_id(flask.session["id"])
        return self.redis.exists(user_hash)

    def get_temp_user(self) -> User | None:
        if "id" not in flask.session or not self.temp_user_exists(flask.session["id"]):
            if current_app.config["CHAT"]["SAFE_MODE"]:
                return None
            else:
                return self.make_temp_user()

        user_id = flask.session["id"]
        conversation = self.get_temp_user_conversation_history(user_id)
        return User(user_id, conversation)

    def make_temp_user(self) -> User:
        user_id = str(uuid4())
        flask.session.permanent = True
        flask.session["id"] = user_id

        self.redis.rpush("users", user_id)
        self.redis.hset(get_user_hash_id(user_id), "join_date", str(datetime.now().isoformat()))

        conversation = self.get_temp_user_conversation_history(user_id)
        return User(user_id, conversation)

    def login(self, auth_code):
        token = self.kc.token(
            grant_type='authorization_code',
            code=auth_code,
            redirect_uri=request.root_url,
        )
        userinfo = self.kc.userinfo(token['access_token'])

        flask.session['user'] = userinfo
        flask.session['token'] = token

        if self.db.user_exists(userinfo['sub']):
            return userinfo
        else:
            self.db.insert_user(userinfo)

        return userinfo

    def logout(self):
        flask.session.clear()
        flask.session.pop('session_key', None)
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
