from uuid import uuid4

import flask
from attr import dataclass
from flask import request, Flask, current_app
from keycloak import KeycloakOpenID
from redis import Redis

from storage.database import DatabaseEngine


@dataclass
class UserMeta:
    username: str
    given_name: str
    family_name: str
    email: str
    roles: list[str]


class User:
    user_id: str
    meta: UserMeta

    def __init__(self, user_id: str, user_meta: UserMeta):
        self.user_id = user_id
        self.meta = user_meta


def get_user_hash_id(user_id: str):
    return f"user_{user_id}"


def get_user_history_ptr(user_id: str):
    conv_id = user_id  # Placeholder until we ID conversations
    return f"history_{user_id}_{conv_id}"


class UserData:
    redis: Redis
    kc: KeycloakOpenID
    db: DatabaseEngine

    def init_app(self, app: Flask, kc: KeycloakOpenID, db: DatabaseEngine):
        self.kc = kc
        self.db = db

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
        return User(user_id)

    def make_temp_user(self) -> User:
        user_id = "temp_" + str(uuid4())
        flask.session.permanent = True
        flask.session["id"] = user_id

        user = User(user_id)
        self.db.insert_user(user)

        return user

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
