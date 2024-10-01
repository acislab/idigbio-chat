from uuid import uuid4

from flask import Flask, jsonify, request, render_template, session, stream_with_context
from flask_cors import CORS
from flask_session import Session

import chat
import search.api
import search.demo
from chat.conversation import Conversation, AiProcessingMessage, stream_response_as_text
from nlp.agent import Agent

app = Flask(__name__, template_folder="templates")
CORS(app, supports_credentials=True)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = "True"
Session(app)

fake_redis = {}

SHOW_PROCESSING_MESSAGES = True
SAFE_MODE = False


def make_user_info():
    user_id = uuid4()
    session["id"] = user_id
    user = {
        "id": user_id,
        "history": Conversation()
    }
    fake_redis[user_id] = user
    return user


def get_user_info() -> dict:
    if "id" not in session or session["id"] not in fake_redis:
        if SAFE_MODE:
            return None
        else:
            return make_user_info()

    user_id = session["id"]
    return fake_redis[user_id]


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})


@app.route("/chat", methods=["POST"])
def chat_api():
    """
    Expects
    { "message": str }

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
    print("REQUEST:", request.json, dict(session), sep="\n")
    agent = Agent()
    user_message = request.json["value"]
    user = get_user_info()
    if user is None:
        if "not a robot" in user_message.lower():
            user = make_user_info()
            message_stream = chat.api.greet(agent, user["history"], "I can confirm that I'm not a robot. Hello!")
        else:
            message_stream = chat.api.are_you_a_robot()
    elif user_message.lower() == "clear":
        fake_redis.pop(user["id"], None)
        message_stream = chat.api.greet(agent, user["history"], "Hello!")
    else:
        message_stream = chat.api.chat(agent, user["history"], user_message)

    if not SHOW_PROCESSING_MESSAGES:
        message_stream = filter(lambda m: not isinstance(m, AiProcessingMessage), message_stream)

    text_stream = stream_response_as_text(message_stream)

    print("RESPONSE:")
    return app.response_class(stream_with_context(text_stream), mimetype="application/json")


@app.route("/search/generate_rq", methods=["POST"])
def generate_rq():
    print("REQUEST:", request.json)
    agent = Agent()
    response = search.api.generate_rq(agent, request.json)
    print("RESPONSE:", response)

    return response


@app.route("/search/update_input", methods=["POST"])
def update_input():
    print("REQUEST:", request.json)
    agent = Agent()
    response = search.api.update_input(agent, request.json)
    print("RESPONSE:", response)

    return response


@app.route("/search/demo/", methods=["GET", "POST"])
def textbox_demo():
    if request.method == "GET":
        return render_template("textbox.html.j2")
    elif request.method == "POST":
        print("REQUEST:", request.form)
        agent = Agent()
        response = search.demo.run(agent, request.form)
        print("RESPONSE:", response)

        return render_template("textbox.html.j2", **response)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")  # , ssl_context='adhoc'
