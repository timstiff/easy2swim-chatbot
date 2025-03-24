from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Use the correct API client and version
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
                "content": f"You are a helpful assistant. Use the following documentation to answer:\n\n{documentation}"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30
