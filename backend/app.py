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
from keycloak.keycloak_openid import KeycloakOpenID
from pydantic.v1.utils import deep_update
from sqlalchemy import create_engine
from typing_extensions import Optional

import chat
import search.api
import search.demo
from chat.messages import AiProcessingMessage, stream_messages
from flask_session import Session
from nlp.ai import AI
from storage.database import DatabaseEngine
from extensions.flask_redis import FlaskRedis
from extensions.user_data import UserData

plan = Blueprint("blueprint", __name__)

redis = FlaskRedis()
user_data = UserData()
ai = AI()


def create_app(config_file: Optional[str] = None, config_dict: Optional[dict] = None,
               database_url=""):
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(plan)

    defaults = {
        "HOST": "0.0.0.0",
        "PORT": 8989,
        "PERMANENT_SESSION_LIFETIME": 2678400,  # In seconds. 2678400 seconds = 31 days.
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": True,
        "SESSION_PERMANENT": False,
        "SESSION_REFRESH_EACH_REQUEST": True,
        "SESSION_TYPE": "redis",
        "CHAT": {
            "SAFE_MODE": True,
            "SHOW_PROCESSING_MESSAGES": True
        },
    }
    app.config.update(defaults)

    if config_file:
        with open(config_file, "rb") as f:
            config_file_content = tomli.load(f, )
            app.config = deep_update(app.config, config_file_content)

    if config_dict:
        app.config = deep_update(app.config, config_dict)

    if "KEYCLOAK" in app.config:
        kc_config = app.config["KEYCLOAK"]
        kc = KeycloakOpenID(
            server_url=kc_config["URL"],
            client_id=kc_config["CLIENT_ID"],
            realm_name=kc_config["REALM_NAME"],
            client_secret_key=os.getenv('KC_SECRET'),
        )
    else:
        kc = None

    CORS(app, supports_credentials=True)
    Session(app)
    redis.init_app(app)

    if database_url:
        engine = create_engine(database_url, echo=True)
        db = DatabaseEngine(engine)
    else:
        db = None

    user_data.init_app(app, redis.inst, kc, db)

    return app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


def get_conversation_id(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if request.json['conversation_id'] != '':
                kwargs['conversation_id'] = request.json['conversation_id']
            else:
                kwargs['conversation_id'] = uuid4()
        except KeyError as e:
            print("No conversation id provided.")
            kwargs['conversation_id'] = uuid4()
        return f(*args, **kwargs)

    return wrapper


def get_public_key():
    url, realm = current_app.config["URL"], current_app.config["REALM_NAME"]
    key_url = f"{url}/realms/{realm}/protocol/openid-connect/certs"
    response = requests.get(key_url)
    keys = response.json()
    # Return the complete key set - python-jose will handle key selection
    return keys


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            # restrict endpoints
            # return jsonify({'message': 'No authorization header'}), 401
            return f(token_payload={}, *args, **kwargs)
        try:
            token = auth_header.split(' ')[1]

            # Debugging
            # unverified_claims = jwt.get_unverified_claims(token)
            # expected_issuer = f"{KEYCLOAK_URL}/realms/{REALM_NAME}"
            # actual_issuer = unverified_claims.get('iss')
            # print(f"Expected issuer: {expected_issuer}")
            # print(f"Actual issuer: {actual_issuer}")

            # Get the unverified headers to find the key ID
            headers = jwt.get_unverified_headers(token)
            kid = headers.get('kid')

            # Get the full JWKS
            jwks = get_public_key()

            # Find the matching key in the JWKS
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == kid:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break

            if not rsa_key:
                return jsonify({'message': 'Unable to find appropriate key'}), 401

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                options={"verify_aud": False},
                issuer=f"{user_data.kc.connection.base_url}/realms/{user_data.kc.realm_name}"
            )
            return f(token_payload=payload, *args, **kwargs)

        except jose.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jose.JWTError as e:
            print(f"JWT Error: {str(e)}")
            return jsonify({'message': 'Invalid token'}), 401

    return decorated


def get_current_user(token_payload: dict):
    return {
        'id': token_payload.get('sub'),
        'name': token_payload.get('sub'),
        'preferred_username': token_payload.get('preferred_username'),
        'given_name': token_payload.get('preferred_username'),
        'family_name': token_payload.get('family_name'),
        'email': token_payload.get('email'),
        'roles': token_payload.get('realm_access', {}).get('roles', [])
    }

@plan.route("/", methods=["GET"])
def home():
    return redirect(url_for("chat"))


@plan.route("/chat-protected", methods=["POST"])
@requires_auth
@get_conversation_id
def chat_api(token_payload: dict, **kwargs):
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
                    "summary": "Here's what I'm doing...",
                    "content": "Here's some markdown"
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
    print("REQUEST:", dict(session), request.json)

    user_message = request.json["value"]
    user = get_current_user(token_payload)
    print(user)

    if user is None:
        return jsonify({'message': 'User must be authenticated to access this endpoint.'}), 401
    else:
        user_id = user['id']
        if not user_data.db.user_exists(user['id']):
            user_data.db.insert_user(user)

        conversation_id = kwargs['conversation_id']
        history = user_data.db.get_or_create_conversation(conversation_id, user_id)

        message_stream = chat.api.chat(ai, history, user_message)

    if not current_app.config["CHAT"]["SHOW_PROCESSING_MESSAGES"]:
        message_stream = filter(lambda m: not isinstance(m, AiProcessingMessage), message_stream)

    text_stream = stream_messages(message_stream)

    return current_app.response_class(stream_with_context(text_stream), mimetype="application/json")


@plan.route("/chat", methods=["POST"])
def chat_unprotected():
    user_message = request.json["value"]
    user = user_data.get_temp_user()
    if user is None:
        if "not a robot" in user_message.lower():
            user = user_data.make_temp_user()
            message_stream = chat.api.greet(ai, user.history, user_message)
        else:
            message_stream = chat.api.are_you_a_robot()
    elif user_message.lower() == "clear":
        user_data.clear_temp_user_history(user.user_id)
        message_stream = chat.api.greet(ai, user.history, "Hello!")
    else:
        message_stream = chat.api.chat(ai, user.history, user_message)

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


@plan.route("/api/login", methods=['POST'])
def login():
    try:
        auth_code = request.json.get('code')
        userinfo = user_data.login(auth_code)

        return jsonify({
            "message": "Login Successful.",
            "user": userinfo
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@plan.route("/api/logout", methods=['POST'])
def logout():
    try:
        user_data.logout()
        return jsonify({"message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


@plan.route("/api/user", methods=['POST'])
def get_user():
    return jsonify(session['user'])


@plan.route('/api/refresh-token', methods=['POST'])
def refresh_token():
    try:
        token = session.get('token', {}).get('refresh_token')
        if not token:
            return jsonify({"error": "No refresh token found"}), 401

        token = user_data.kc.refresh_token(token)
        session['token'] = token

        return jsonify({
            "message": "Token Refreshed.",
            "token": token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@plan.route("/api/conversations", methods=['POST'])
@requires_auth
def get_conversations(token_payload: dict):
    try:
        user_id = get_current_user(token_payload)['id']
        user_conversations = user_data.db.get_user_conversations(user_id)
        print(user_id)
        return jsonify({
            "user": session.get('user'),
            "history": user_conversations
        })
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


@plan.route("/api/get-conversation", methods=['POST'])
@requires_auth
@get_conversation_id
def get_conversation(**kwargs):
    try:
        if kwargs['conversation_id'] is None or '':
            return {"Invalid conversation id"}, 400
        
        user_id = get_current_user()['id']
        conversation_id = kwargs['conversation_id']

        conversation = user_data.db.get_conversation_messages(conversation_id)
        
        return jsonify({
            "user": user_id,
            "history": conversation
        })
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    load_dotenv()

    database_url = (f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}:"
                    f"{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}?sslmode=disable")

    app = create_app("config.toml", database_url=database_url)
    app.run(debug=True, port=app.config["PORT"], host=app.config["HOST"])  # , ssl_context='adhoc'
