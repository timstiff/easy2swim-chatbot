import openai
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Preloaded welcome message and manual content
welcome_message = "Welcome to Easy2Swim. If you are looking for swimming lessons please give me the age of the swimmer/s and experience or just ask a question."
manual_content = """
You are the Easy2Swim Assistant. Use the following manual to answer questions:
- **Class Recommendations**: Always ask for and confirm BOTH the child’s age and their swimming ability before recommending a class.
- **Class Information**: Provide information about the various class options such as Starfish, Turtle, Stingray, and more.
- **Pricing & Payments**: Explain the payment structure including sibling discounts and payment terms.
- **General Info**: Provide details about the swim school, facilities, free assessments, swim nappies, and more.

Topics You Handle:
- Swim Lessons & Programmes
- Age Groups & Class Placement
- Pricing & Payments
- Schedules & Public Holidays
- Free Assessments
- Booking Procedures
- Swim Nappies & Gate Code
- Splash Park
- Water Aerobics
- Adult & Private Lessons

For questions you can’t answer or need Tim’s confirmation, refer the customer to Tim via WhatsApp: https://wa.me/27824468902.
"""

# A simple way to store the conversation history
conversation_history = []

@app.route("/")
def home():
    return "Easy2Swim Chatbot API is running!"

@app.route("/ask", methods=["POST"])
def ask():
    global conversation_history
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        user_message = data.get("message")
        
        if user_message is None:
            return jsonify({"error": "Missing message"}), 400

        # Add welcome message as first entry if history is empty
        if len(conversation_history) == 0:
            conversation_history.append({"role": "system", "content": welcome_message})

        # Add the manual as a system message at the start
        if len(conversation_history) == 1:
            conversation_history.append({"role": "system", "content": manual_content})

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message})

        # Call OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )

        bot_response = response['choices'][0]['message']['content']
        
        # Add bot response to the history
        conversation_history.append({"role": "assistant", "content": bot_response})

        return jsonify({"reply": bot_response})

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route("/clear", methods=["POST"])
def clear_history():
    global conversation_history
    conversation_history = []  # Clear the conversation history
    return jsonify({"message": "Conversation history cleared"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
