from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import search.api
import search.demo
from chat.agent import Agent
from chat.plan_response import ask_llm_to_call_a_function
from chat.types import Conversation

app = Flask(__name__, template_folder="templates")
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data["message"]

    agent = Agent()

    convo: Conversation = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = ask_llm_to_call_a_function(agent, convo)

    # generated_query = json.dumps(generate_query(user_text).model_dump(exclude_none=True))

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
    response = search.api.update_input(agent, request.json).model_dump(exclude_none=True)
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
