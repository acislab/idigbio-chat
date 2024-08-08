import json

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import idigbio_util
from chat.agent import Agent
from chat.types import Conversation
from chat.plan_response import ask_llm_to_call_a_function

import search.api

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
    data = request.json
    agent = Agent()
    response = search.api.generate_rq(agent, data)
    return response


@app.route("/search/update_input", methods=["POST"])
def update_input():
    data = request.json
    agent = Agent()
    response = search.api.update_input(agent, data)
    return response


@app.route("/search/demo", methods=["GET", "POST"])
def textbox_demo():
    if request.method == "GET":
        return render_template("textbox.html")
    elif request.method == "POST":
        print(request.form)

        data = request.form

        agent = Agent()
        response = {}
        if data["action"] == "generate_rq":
            response = search.api.generate_rq(agent, data)
        elif data["action"] == "update_input":
            response = search.api.update_input(agent, data)

        rq = json.dumps(response["rq"]) if type(response["rq"]) == dict else response["rq"]
        params = {"rq": response["rq"]}
        url_params = idigbio_util.url_encode_params(params)

        input = response["input"]
        message = response["message"]

        return render_template("textbox.html",
                               portal_url=f"https://beta-portal.idigbio.org/portal/search?{url_params}",
                               api_url=f"https://search.idigbio.org/v2/search/records?{url_params}",
                               input=input,
                               rq=rq,
                               message=message)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
