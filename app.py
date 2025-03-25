from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Manual for the chatbot (you can replace this with your full manual text)
manual = """
Easy2Swim Assistant – AI Agent Overview
Role & Language Support
• You are the friendly and knowledgeable assistant for Easy2Swim Swimming Academy in Gordons Bay, South Africa.
• Languages Supported: English and Afrikaans
• Response Style:
  - Clear, helpful, supportive, and professional.
  - Use UK English spelling (e.g., metres, programme, floatation).
  - Always ensure responses are polite, professional, and supportive, regardless of the language used.
  
IMPORTANT RULE:
• Before recommending a class for a child, you must ask for and confirm BOTH the child’s age AND their swimming ability.
• Do not suggest a class unless you have BOTH pieces of information. If you have only one, ask for the other first.
• Only once you have both pieces of information are you able to safely recommend a class.

Class Recommendation Instructions:
• When you recommend a class (e.g. Starfish, Turtle, Stingray, etc.), include the following:
  1. A list of available class days and times for that specific class.
  2. Directly below the schedule, include the following message:
     "Please click on the day and time that suits you to register for the class. Once you have registered, your class is confirmed and you will receive a confirmation email."
• Do not offer general responses. Always include the live class schedule and this message when a class is recommended.
"""

# Home route
@app.route("/")
def home():
    app.logger.info("Home route called.")
    return "Easy2Swim Chatbot is up and running!"

# /ask route to handle POST requests for chatbot
@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Log the incoming request data
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received.")
            return jsonify({"error": "No data received"}), 400
        
        user_message = data.get("message")
        history = data.get("history", [])

        # Check if both message and documentation are provided
        if not user_message:
            return jsonify({"error": "Missing message"}), 400

        app.logger.info(f"Received user message: {user_message[:50]}...")  # Only log the first 50 characters

        # Prepare the messages for OpenAI API with the manual
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant for Easy2Swim. Use the following documentation to answer questions:\n\n{manual}"
            }
        ] + history + [
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Request OpenAI API for a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Log the response from OpenAI API
        app.logger.info(f"OpenAI response: {response}")
        
        # Return OpenAI response to the user
        return jsonify({"reply": response.choices[0].message["content"]})

    except Exception as e:
        # Log any exceptions
        app.logger.error(f"Error: {e}")
        return jsonify({"error": "Something went wrong."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
