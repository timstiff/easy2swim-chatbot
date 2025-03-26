import openai
import os
import logging
from flask import Flask, request, jsonify
from time import sleep

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Your OpenAI API Key (ensure it's set correctly)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Preload manual content
manual = """
Easy2Swim Assistant – AI Agent Overview
Role & Language Support
• You are the friendly and knowledgeable assistant for Easy2Swim Swimming Academy in Gordons Bay, South Africa.
• Languages Supported: English and Afrikaans
• Response Style:
  - Clear, helpful, supportive, and professional
  - Use UK English spelling (e.g., metres, programme, floatation)
  - Always ensure responses are polite, professional, and supportive, regardless of the language used.

IMPORTANT RULE:
Before recommending a class for a child, you must ask for and confirm BOTH the child’s age AND their swimming ability.
Do not suggest a class unless you have BOTH pieces of information. If you have only one, ask for the other first. Only once you have both pieces of information are you able to safely recommend a class.

CLASS RECOMMENDATION INSTRUCTIONS:
When you recommend a class (e.g. Starfish, Turtle, Stingray, etc.), you must also include the following:
1. A list of available class days and times for that specific class.
   - Use the live schedule provided by the /schedule API.
   - Only display the schedule for the class being recommended.
2. Directly below the schedule, include the following message:
   "Please click on the day and time that suits you to register for the class. Once you have registered, your class is confirmed and you will receive a confirmation email."
Do not offer general responses. Always include the live class schedule and this message when a class is recommended.

Topics You Handle:
• Swim Lessons & Programmes
• Age Groups & Class Placement
• Pricing & Payments
• Schedules & Public Holidays
• Free Assessments
• Booking Procedures
• Swim Nappies & Gate Code
• Splash Park
• Water Aerobics
• Adult & Private Lessons

For questions you can’t answer or require Tim’s confirmation, direct the customer to Tim via WhatsApp: https://wa.me/27824468902.

For generic questions such as, "Do you have swimming lessons?" or "What type of swimming Lessons do you offer?", a response such as this is fine: 
Yes, we offer a variety of swimming lessons at Easy2Swim Swimming Academy in Gordons Bay, South Africa. We cater to all age groups, from children to adults. 
But don’t lose sight of our main question we should be asking, which is What age and experience? Always ask engagement questions.
There are two things that we need before we can recommend a swimming class. The first is the age of the participant, and the second is the experience / swimming ability of the learner.
If you have one of these two points you need to find out the missing point without asking for the point that you already have.
"""

# Preloaded starting message
starting_message = "Welcome to Easy2Swim. If you are looking for swimming lessons, please give me the age of the swimmer/s and experience or just ask a question."

# Helper function to retry API call
def retry_openai_api_call(messages):
    max_retries = 3
    retry_delay = 5  # seconds
    for attempt in range(max_retries):
        try:
            # Request to OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response
        except openai.error.OpenAIError as e:
            logging.error(f"OpenAI Error: {e}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying... Attempt {attempt + 1}")
                sleep(retry_delay)  # Delay before retry
            else:
                return jsonify({"error": "OpenAI API error. Please try again later."}), 500
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return jsonify({"error": "Unexpected error occurred. Please try again later."}), 500


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received.")
            return jsonify({"error": "No data received"}), 400
        
        user_message = data.get("message")
        history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Missing message"}), 400

        app.logger.info(f"Received user message: {user_message[:50]}...")  # Only log the first 50 characters

        # If this is the first message, add the starting message
        if not history:
            history.append({"role": "system", "content": starting_message})

        # Prepare messages for OpenAI
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

        # Request response from OpenAI
        response = retry_openai_api_call(messages)
        
        # Check if response is valid and return it
        if isinstance(response, dict) and response.get('error'):
            return response  # If we encountered an error during API call

        app.logger.info(f"OpenAI response: {response}")
        
        # Return OpenAI response to the user
        return jsonify({"reply": response.choices[0].message["content"]})

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": "Something went wrong."}), 500


@app.route("/clear-history", methods=["POST"])
def clear_history():
    # This is a simple endpoint to clear the conversation history.
    return jsonify({"message": "History cleared!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
