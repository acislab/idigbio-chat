from flask import Flask, jsonify, request
from flask_cors import CORS

from llm_actions.plan_response import ask_llm_to_call_a_function

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data["message"]

    response = ask_llm_to_call_a_function(user_message)

    # generated_query = json.dumps(generate_query(user_text).model_dump(exclude_none=True))

    return {"response": response}


if __name__ == '__main__':
    app.run(debug=True, port=8080)
