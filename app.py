from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    app.logger.info("Home route called.")
    return "Easy2Swim Chatbot API is running!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Log received data for debugging purposes
        app.logger.debug(f"Received data: {data}")
        
        # Check if data is missing message or documentation
        if not data or 'message' not in data or 'documentation' not in data:
            app.logger.error("Missing message or documentation in request data.")
            return jsonify({"error": "Missing message or documentation"}), 400
        
        # Extract message, documentation, and history
        user_message = data.get("message")
        documentation = data.get("documentation")
        history = data.get("history", [])

        # Log user message and documentation for debugging
        app.logger.info(f"Received user message: {user_message[:50]}...")  # Only log the first 50 characters
        app.logger.info(f"Received documentation: {documentation[:50]}...")  # Only log first 50 chars

        # Prepare the messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": f"You are the Easy2Swim Assistant. Use the following manual to answer questions:\n\n{documentation}"
            }
        ] + history + [
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Ensure OpenAI API key is set correctly
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Make request to OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Log OpenAI response for debugging
        app.logger.info(f"OpenAI response: {response}")
        
        # Return OpenAI response to the user
        return jsonify({"reply": response.choices[0].message["content"]})

    except Exception as e:
        # Log the error if something goes wrong
        app.logger.error(f"Error: {e}")
        return jsonify({"error": "Something went wrong."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
