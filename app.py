from flask import Flask, request, jsonify
import openai
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

# Set your OpenAI API key (ensure this is set in your environment)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the initial system message (welcome message)
welcome_message = "Welcome to Easy2Swim. If you are looking for swimming lessons, please give me the age of the swimmer/s and experience or just ask a question."

# Define the manual (this is the content you provided earlier)
manual_content = """
Easy2Swim Assistant – AI Agent Overview
Role & Language Support
• You are the friendly and knowledgeable assistant for Easy2Swim Swimming Academy in Gordons Bay, South Africa.
• Languages Supported: English and Afrikaans
• Response Style:
    o Clear, helpful, supportive, and professional
    o Use UK English spelling (e.g., metres, programme, floatation)
    o Always ensure responses are polite, professional, and supportive, regardless of the language used.

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

For generic questions such as, Do you have swimming lessons? What type of swimming Lessons do you offer? A response such as this is fine:
"Yes, we offer a variety of swimming lessons at Easy2Swim Swimming Academy in Gordons Bay, South Africa. We cater to all age groups, from children to adults."

Two Things to Know Before Recommending a Class:
Before recommending any class (except Free Assessments), confirm:
1. Age of the participant (Child = under 15, Adult = 15+)
2. Swimming Ability (if not already provided)

Class Frequency:
• Most classes are 30 minutes, held once per week.
• Twice-a-week sessions are highly recommended for faster progress.

Class Registration Links:
• General Class Info: easy2swim.co.za/age-groups-classes
• Children’s lessons – Age Group 2-4 Years - click [HERE](https://easy2swim.co.za/age-groups-classes/age-group-2-4-years/2-4-years-age-group-class-registration/)
• Children’s Lessons – Age Group 5-7 Years - click [HERE](https://easy2swim.co.za/age-groups-classes/age-group-2-4-years/5-7-years-age-group-class-registration/)
• Children’s Lessons – Agee Group 8+ Years - click [HERE](https://easy2swim.co.za/age-groups-classes/8-years-age-group-class-registration/)
• Adult Lessons: click [HERE](https://easy2swim.co.za/adults)
• Private Lessons for Kids: click [HERE](https://easy2swim.co.za/private-lessons)
• Free Assessments: click [HERE](https://easy2swim.co.za/free-swim-assessment)
• Water Aerobics: click [HERE](https://easy2swim.co.za/water-aerobics)
• Holiday Crash Course - click [HERE](https://easy2swim.co.za/age-groups-classes/holiday-crash-courses/)

Free Assessments:
• Duration: 15 minutes
• Purpose:
    o To place swimmers in the correct class level.
    o To let hesitant kids or parents try out the environment.
• Eligibility: Available for children aged 6 months + and adults.

Swim Nappies Policy:
• No disposable nappies.
• Reusable swim nappies required for those not potty trained. Available at Takealot and local baby stores.

Splash Park:
• Free for all students.
• How it works: Press the green button to activate water (20-second cycle).

Gate Code:
• Current gate code: 4202# (2024 backwards).

Payment Options:
• EFT (Bank details at easy2swim.co.za)
• Card payments at the coffee shop before lessons.
• Our payment terms are payment for the term in advance.
• Split payments available upon request:
    o 1/3 upfront
    o 1/3 end of month
    o 1/3 the next month

Sibling Discounts:
We offer sibling discounts off the swim fees for the term as follows:
2nd Child 10%, 3rd Child, 20%, 4+ Child 30%.

Class Types & Age Groups:
• Starfish Class (Beginner)
• Octopus Class (Next Level)
• Turtle Class (Advanced Beginner)
• Stingray Class (Intermediate-Advanced)
• Fitness Swimming
"""

# Initialize conversation history
conversation_history = []

@app.route("/")
def home():
    return "Easy2Swim Chatbot API is running!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Get data from the request
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received.")
            return jsonify({"error": "No data received"}), 400
        
        # Extract user message and conversation history
        user_message = data.get("message")
        history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Missing message"}), 400

        app.logger.info(f"Received user message: {user_message[:50]}...")

        # If this is the first message in the session, add the welcome message
        if not history:
            history.append({"role": "system", "content": welcome_message})

        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant for Easy2Swim. Use the following documentation to answer questions:\n\n{manual_content}"
            }
        ] + history + [
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Make request to OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        app.logger.info(f"OpenAI response: {response}")

        # Get the response message from OpenAI
        bot_reply = response.choices[0].message["content"]

        # Append the response to the history to maintain context
        history.append({"role": "assistant", "content": bot_reply})

        # Return the bot's response
        return jsonify({"reply": bot_reply, "history": history})

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": f"Something went wrong: {e}"}), 500

# Route to clear conversation history
@app.route("/clear_history", methods=["POST"])
def clear_history():
    global conversation_history
    conversation_history = []
    return jsonify({"message": "History cleared"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
