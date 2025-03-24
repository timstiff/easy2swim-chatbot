
from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "Easy2Swim Chatbot API is running!"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_message = data.get("message")
    documentation = data.get("documentation")

    if not user_message or not documentation:
        return jsonify({"error": "Missing message or documentation"}), 400

    try:
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Use the following documentation to answer:

{documentation}"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
