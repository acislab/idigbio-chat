from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
from flask_session import Session

import search.api
import search.demo
from nlp.agent import Agent

app = Flask(__name__, template_folder="templates")
CORS(app)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})


@app.route("/chat", methods=["POST"])
def chat():
    print("REQUEST:", request.json)
    user_message = request.json["message"]

    history = session.get("history", [])
    agent = Agent()
    response = chat.api.chat(agent, history, user_message)

    session["history"] = history

    print("RESPONSE:", response)
    return {"response": response}


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


@app.route("/search/demo", methods=["GET", "POST"])
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
    app.run(debug=True, port=8081, host="0.0.0.0")
