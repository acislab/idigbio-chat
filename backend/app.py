import tomli
from flask import Flask, jsonify, request, render_template, session, stream_with_context
from flask_cors import CORS

import chat
import search.api
import search.demo
import redis as r
from chat.messages import AiProcessingMessage, stream_messages
from flask_session import Session
from nlp.agent import Agent
from storage.fake_redis import FakeRedis
from storage.user_data import UserData

app = Flask(__name__, template_folder="templates")
CORS(app, supports_credentials=True)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = "True"
app.config.from_file("config.toml", tomli.load, text=False)
Session(app)

chat_config = app.config["CHAT"]
redis_config = chat_config["REDIS"]

if redis_config["PORT"] == 0:
    redis = FakeRedis().redis
else:
    redis = r.Redis(port=redis_config["PORT"])

user_data = UserData(session, redis, chat_config)


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
    print("REQUEST:", dict(session), request.json)
    agent = Agent()
    user_message = request.json["value"]
    user = user_data.get_user()
    if user is None:
        if "not a robot" in user_message.lower():
            user = user_data.make_user()
            message_stream = chat.api.greet(agent, user.history, "I confirm that I'm not a robot. Hello!")
        else:
            message_stream = chat.api.are_you_a_robot()
    elif user_message.lower() == "clear":
        user_data.clear_stored_user_history(user.user_id)
        message_stream = chat.api.greet(agent, user.history, "Hello!")
    else:
        message_stream = chat.api.chat(agent, user.history, user_message)

    if not chat_config["SHOW_PROCESSING_MESSAGES"]:
        message_stream = filter(lambda m: not isinstance(m, AiProcessingMessage), message_stream)

    text_stream = stream_messages(message_stream)

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
    app.run(debug=True, port=chat_config["SERVER"]["PORT"], host="0.0.0.0")  # , ssl_context='adhoc'
