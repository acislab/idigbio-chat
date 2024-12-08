import os
from functools import wraps
from uuid import uuid4

import jose
import requests
import tomli
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, stream_with_context, redirect, url_for, current_app, \
    Blueprint, session
from flask_cors import CORS
from jose import jwt
from keycloak import KeycloakOpenID
from pydantic.v1.utils import deep_update
from sqlalchemy import create_engine
from typing_extensions import Optional

import chat
import search.api
import search.demo
from chat.messages import AiProcessingMessage, stream_messages
from extensions.flask_redis import FlaskRedis
from extensions.user_data import UserData, UserMeta, User
from flask_session import Session
from nlp.ai import AI
from storage.database import DatabaseEngine

redis = FlaskRedis()
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
        app.config.update(defaults)

    if config_dict:
        app.config = deep_update(app.config, config_dict)

    if "KEYCLOAK" in app.config:
        kc_config = app.config["KEYCLOAK"]
        kc = KeycloakOpenID(
            server_url=kc_config["URL"],
            client_id=kc_config["CLIENT_ID"],
            realm_name=kc_config["REALM_NAME"],
            client_secret_key=os.getenv("KC_SECRET"),
        )
    else:
        kc = None

    redis.init_app(app)

    user_data.init_app(app, kc, database)

    CORS(app, supports_credentials=True)
    Session(app)

    return app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


def get_conversation_id(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Is conversation_id ever an empty string? If not, we can just do:
        #  conversation_id = request.json.get("conversation_id", uuid4())

        conversation_id = request.json.get("conversation_id")
        if not conversation_id:
            conversation_id = str(uuid4())

        return f(*args, conversation_id=conversation_id, **kwargs)

    return wrapper


def get_public_key():
    url, realm = current_app.config["KEYCLOAK"]["URL"], current_app.config["KEYCLOAK"]["REALM_NAME"]
    key_url = f"{url}/realms/{realm}/protocol/openid-connect/certs"
    response = requests.get(key_url)
    keys = response.json()
    # Return the complete key set - python-jose will handle key selection
    return keys


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            # restrict endpoints
            # return jsonify({"message": "No authorization header"}), 401
            return f(user={}, *args, **kwargs)
        try:
            token = auth_header.split(" ")[1]

            # Debugging
            # unverified_claims = jwt.get_unverified_claims(token)
            # expected_issuer = f"{KEYCLOAK_URL}/realms/{REALM_NAME}"
            # actual_issuer = unverified_claims.get("iss")
            # print(f"Expected issuer: {expected_issuer}")
            # print(f"Actual issuer: {actual_issuer}")

            # Get the unverified headers to find the key ID
            headers = jwt.get_unverified_headers(token)
            kid = headers.get("kid")

            # Get the full JWKS
            jwks = get_public_key()

            # Find the matching key in the JWKS
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break

            if not rsa_key:
                return jsonify({"message": "Unable to find appropriate key"}), 401

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
                issuer=f"{user_data.kc.connection.base_url}/realms/{user_data.kc.realm_name}"
            )

            user_id, user_meta = read_user_token_payload(payload)
            user = User(user_id, user_meta)

            return f(user=user, *args, **kwargs)

        except jose.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jose.JWTError as e:
            print(f"JWT Error: {str(e)}")
            return jsonify({"message": "Invalid token"}), 401

    return decorated


def read_user_token_payload(token_payload: dict) -> (str, UserMeta):
    user_id = token_payload.get("sub")
    return (
        user_id,
        UserMeta(
            username=token_payload.get("preferred_username"),
            given_name=token_payload.get("preferred_username"),
            family_name=token_payload.get("family_name"),
            email=token_payload.get("email"),
            roles=token_payload.get("realm_access", {}).get("roles", [])
        )
    )


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
    # print("REQUEST:", dict(session), request.json)

    user_message = request.json["value"]
    print(user)

    if user is None:
        return jsonify({"message": "User must be authenticated to access this endpoint."}), 401
    else:
        if not user_data.db.user_exists(user.user_id):
            return jsonify({"message": "Something went wrong. Try logging in again."}), 500

        conversation = user_data.db.get_or_create_conversation(conversation_id, user.user_id)

        message_stream = chat.api.chat(ai, conversation, user_message)

    if not current_app.config["CHAT"]["SHOW_PROCESSING_MESSAGES"]:
        message_stream = filter(lambda m: not isinstance(m, AiProcessingMessage), message_stream)

    text_stream = stream_messages(message_stream)

    return current_app.response_class(stream_with_context(text_stream), mimetype="application/json")


@plan.route("/chat", methods=["POST"])
@get_conversation_id
def chat_unprotected(conversation_id: str):
    user_message = request.json["value"]
    user = user_data.get_temp_user()
    if user is None:
        if "not a robot" in user_message.lower():
            user = user_data.make_temp_user()
            conversation = user_data.db.get_or_create_conversation(conversation_id, user.user_id)
            message_stream = chat.api.greet(ai, conversation, user_message)
        else:
            message_stream = chat.api.are_you_a_robot()
    else:
        conversation = user_data.db.get_or_create_conversation(conversation_id, user.user_id)
        message_stream = chat.api.chat(ai, conversation, user_message)

    if not current_app.config["CHAT"]["SHOW_PROCESSING_MESSAGES"]:
        message_stream = filter(lambda m: not isinstance(m, AiProcessingMessage), message_stream)

    text_stream = stream_messages(message_stream)

    return current_app.response_class(stream_with_context(text_stream), mimetype="application/json")


@plan.route("/search/generate_rq", methods=["POST"])
def generate_rq():
    print("REQUEST:", request.json)
    ai = AI()
    response = search.api.generate_rq(ai, request.json)
    print("RESPONSE:", response)

    return response


@plan.route("/search/update_input", methods=["POST"])
def update_input():
    print("REQUEST:", request.json)
    ai = AI()
    response = search.api.update_input(ai, request.json)
    print("RESPONSE:", response)

    return response


@plan.route("/search/demo/", methods=["GET", "POST"])
def textbox_demo():
    if request.method == "GET":
        return render_template("textbox.html.j2")
    elif request.method == "POST":
        print("REQUEST:", request.form)
        ai = AI()
        response = search.demo.run(ai, request.form)
        print("RESPONSE:", response)

        return render_template("textbox.html.j2", **response)


@plan.route("/api/login", methods=["POST"])
def login():
    auth_code = request.json.get("code")
    userinfo = user_data.login(auth_code)

    return jsonify({
        "message": "Login Successful.",
        "user": userinfo
    })


@plan.route("/api/logout", methods=["POST"])
def logout():
    user_data.logout()
    return jsonify({"message": "Logged out successfully"})


@plan.route("/api/user", methods=["POST"])
def get_user():
    return jsonify(session["user"])


@plan.route("/api/refresh-token", methods=["POST"])
def refresh_token():
    token = session.get("token", {}).get("refresh_token")
    if not token:
        return jsonify({"error": "No refresh token found"}), 401

    token = user_data.kc.refresh_token(token)
    session["token"] = token

    return jsonify({
        "message": "Token Refreshed.",
        "token": token
    })


@plan.route("/api/conversations", methods=["POST"])
@requires_auth
def get_conversations(user: User):
    user_conversations = user_data.db.get_user_conversations(user.user_id)
    return jsonify({
        "user": user.user_id,
        "history": user_conversations
    })


@plan.route("/api/get-conversation", methods=["POST"])
@requires_auth
@get_conversation_id
def get_conversation(user: User, conversation_id: str):
    if not conversation_id:
        return jsonify({"error": "Invalid conversation id"}), 400

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
