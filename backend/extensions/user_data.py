from typing import Optional
from uuid import uuid4

import flask
from attr import dataclass
from flask import request, Flask, current_app
from keycloak import KeycloakOpenID

from storage.database import DatabaseEngine


@dataclass
class UserMeta:
    username: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    email: Optional[str]
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


empty_user_meta = UserMeta(
    username=None,
    given_name=None,
    family_name=None,
    email=None,
    roles=[]
)


class UserData:
    _kc: KeycloakOpenID
    _db: DatabaseEngine

    def init_app(self, app: Flask, kc: KeycloakOpenID, db: DatabaseEngine):
        self._kc = kc
        self._db = db

    def user_exists(self, user_id: str, temp: bool):
        if temp:
            return self._db.temp_user_exists(user_id)
        else:
            return self._db.user_exists(user_id)

    def get_temp_user(self) -> User | None:
        if "id" not in flask.session or not self.user_exists(flask.session["id"], True):
            if current_app.config["CHAT"]["SAFE_MODE"]:
                return None  # Defer user creation until passing the robo check
            else:
                return self.make_temp_user()

        user_id = flask.session["id"]

        return User(user_id, empty_user_meta)

    def make_temp_user(self) -> User:
        user_id = str(uuid4())

        flask.session.permanent = True
        flask.session["id"] = user_id

        user = User(user_id, empty_user_meta)
        self._db.insert_user({
            "id": user_id,
            "temp": True
        })

        return user

    def login(self, auth_code):
        token = self._kc.token(
            grant_type="authorization_code",
            code=auth_code,
            redirect_uri=request.root_url,
        )
        userinfo = self._kc.userinfo(token["access_token"])

        flask.session["user"] = userinfo
        flask.session["token"] = token

        if not self._db.user_exists(userinfo["sub"]):
            self._db.insert_user(userinfo)

        return userinfo

    def logout(self):
        flask.session.clear()
        flask.session.pop("session_key", None)
        self._kc.logout(refresh_token=None)

    def stream_conversation_for_frontend(self, conversation_id: str):
        return self._db.stream_conversation_for_frontend(conversation_id)

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
