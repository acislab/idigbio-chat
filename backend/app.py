import os
from functools import wraps
from typing import Iterator
from uuid import uuid4

import tomli
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, stream_with_context, redirect, url_for, current_app, \
    Blueprint, session
from flask_cors import CORS
from pydantic.v1.utils import deep_update
from sqlalchemy import create_engine
from typing_extensions import Optional

import chat
from chat.messages import stream_messages, Message
from extensions.flask_redis import FlaskRedis
from extensions.user_auth import UserAuth, AuthenticationError
from extensions.user_data import UserData, User
from flask_session import Session
from nlp.ai import AI
from storage.database import DatabaseEngine

redis = FlaskRedis()
user_auth = UserAuth()
user_data = UserData()
ai = AI()

plan = Blueprint("blueprint", __name__)


def handle_error(e: Exception):
    return jsonify(message="Something went wrong.", error=str(e)), 500


def create_app(config_dict: Optional[dict], database: DatabaseEngine):
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(plan)
    app.register_error_handler(Exception, handle_error)

    with open("../config.toml.template", "rb") as f:
        defaults = tomli.load(f)
        app.config = deep_update(app.config, defaults)

    if config_dict:
        app.config = deep_update(app.config, config_dict)

    redis.init_app(app)
    user_auth.init_app(app)
    user_data.init_app(app, database)

    CORS(app, supports_credentials=True)
    Session(app)

    return app


def get_conversation_id(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        conversation_id = request.json.get("conversation_id", str(uuid4()))
        return f(*args, conversation_id=conversation_id, **kwargs)

    return wrapper


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return f(user=None, *args, **kwargs)

        try:
            token = auth_header.split(" ")[1]
            user = user_auth.authenticate(token)
            return f(user=user, *args, **kwargs)
        except AuthenticationError as e:
            print(e)
            return f(user=None, *args, **kwargs)

    return decorated


@plan.route("/", methods=["GET"])
def home():
    return redirect(url_for("chat"))


@plan.route("/chat-protected", methods=["POST"])
@requires_auth
@get_conversation_id
def chat_api(user: User, conversation_id: str):
    """
    Expects
    { "type" str, "value": str | dict }

    Returns one or more
    [{ "type": str, "value": str | dict }]
    See chat.conversation.MessageType
    The whole response is streamed. For each message, "type" is always sent before "value".

    Example:
        Request:
        {
            "type": "user_text_message",
            "value": "Show a map of genus Carex"
        }

        Response:
        [
            {
                "type": "ai_processing_message",
                "value": {
                    "summary": "Here"s what I"m doing...",
                    "content": "Here"s some markdown"
                }
            },
            {
                "type": "ai_map_message,
                "value": {
                    "rq": {
                        "genus": "Carex"
                    }
                }
            }
        ]
    """
    user_message = request.json["value"]
    print(user)

    if user is None:
        return jsonify(error="Unauthorized"), 401

    if not user_data.user_exists(user.user_id, temp=False):
        return jsonify({"message": "Something went wrong. Try logging in again."}), 500

    message_stream = _build_chat_response(user, conversation_id, user_message)
    text_stream = stream_messages(message_stream)

    return current_app.response_class(stream_with_context(text_stream), mimetype="application/json")


@plan.route("/chat", methods=["POST"])
@get_conversation_id
def chat_unprotected(conversation_id: str):
    user_message = request.json.get("value", "")
    user = user_data.get_temp_user()

    if user_message and "not a robot" in user_message.lower():
        user = user_data.make_temp_user()

    message_stream = _build_chat_response(user, conversation_id, user_message)
    text_stream = stream_messages(message_stream)

    return current_app.response_class(stream_with_context(text_stream), mimetype="application/json")


def _build_chat_response(user: User, conversation_id: str, user_message: Optional[str]) -> Iterator[
    Message]:
    if not user_message and current_app.config["CHAT"]["SHOW_INTRO_MESSAGE"]:
        yield from chat.api.intro()

    if user is None:
        yield from chat.api.are_you_a_robot()
        return

    if user_message:
        conversation = user_data.get_or_create_conversation(conversation_id, user.user_id)
        yield from chat.api.chat(ai, conversation, user_message)


@plan.route("/login", methods=["POST"])
def login():
    auth_code = request.json.get("code")
    userinfo = user_auth.login(auth_code)
    user_data.register_user(userinfo)

    return jsonify({
        "message": "Success",
        "user": userinfo
    })


@plan.route("/logout", methods=["POST"])
def logout():
    session.clear()
    user_auth.logout()
    return jsonify({"message": "Success"})


@plan.route("/user", methods=["POST"])
def get_user():
    return jsonify(session["user"])


@plan.route("/refresh-token", methods=["POST"])
def refresh_token():
    token = session.get("token", {}).get("refresh_token")
    if not token:
        return jsonify({"error": "No refresh token found"}), 401

    token = user_auth.refresh_token(token)
    session["token"] = token

    return jsonify({
        "message": "Token Refreshed.",
        "token": token
    })


@plan.route("/conversations", methods=["POST"])
@requires_auth
def get_conversations(user: User):
    if not user:
        return jsonify(error="Unauthorized"), 401

    user_conversations = user_data.get_user_conversations(user.user_id)
    return jsonify({
        "user": user.user_id,
        "history": user_conversations
    })


@plan.route("/get-conversation", methods=["POST"])
@requires_auth
@get_conversation_id
def get_conversation(user: User, conversation_id: str):
    if not user:
        return jsonify(error="Unauthorized"), 401

    if not conversation_id:
        return jsonify(error="Invalid conversation id"), 400

    conversation = list(user_data.stream_conversation_for_frontend(conversation_id))

    return jsonify({
        "user": user.user_id,
        "history": conversation
    })


if __name__ == "__main__":
    load_dotenv()

    with open("../config.toml", "rb") as f:
        config = tomli.load(f)

    database_url = (f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:"
                    f"{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}?sslmode=disable")

    engine = create_engine(database_url, echo=True)
    db = DatabaseEngine(engine)

    app = create_app(config, database=db)
    app.run(debug=True, port=app.config["PORT"], host=app.config["HOST"])  # , ssl_context="adhoc"
