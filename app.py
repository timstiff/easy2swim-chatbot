from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging
import signal
import sys

# Create the Flask app
app = Flask(__name__)

# Enable CORS for all routes and only allow requests from https://easy2swim.co.za
CORS(app, origins=["https://easy2swim.co.za"], supports_credentials=True)

# Set up logging to capture detailed information
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture detailed logs

# Signal handling to log shutdown reasons
def shutdown_signal_handler(signal, frame):
    app.logger.info("Received shutdown signal. Flask is shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_signal_handler)

# Log startup when the app is initialized
app.logger.info("Flask app initialized and ready to accept requests.")

@app.route("/")
def home():
    app.logger.info("Home route called.")
    return "Easy2Swim Chatbot API is running!"

# Handle OPTIONS request (CORS Preflight)
@app.route("/api/ask", methods=["OPTIONS"])
def handle_options():
    app.logger.info("Handling OPTIONS request for /api/ask")
    return "", 200  # Respond with 200 OK to preflight requests

@app.route("/api/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        app.logger.debug(f"Received data: {data}")  # Log the entire request data
        
        if not data:
            app.logger.error("No JSON data received.")
            return jsonify({"error": "No data received"}), 400
        
        user_message = data.get("message")
        documentation = data.get("documentation")
        history = data.get("history", [])

        if not user_message or not documentation:
            app.logger.error(f"Missing message or documentation: {data}")
            return jsonify({"error": "Missing message or documentation"}), 400

        app.logger.info(f"User message: {user_message[:50]}...")
        app.logger.info(f"Documentation: {documentation[:50]}...")

        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant for Easy2Swim. Use the following documentation to answer questions:\n\n{documentation}"
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
        app.logger.debug(f"Sending request to OpenAI API with {len(messages)} messages")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        app.logger.debug(f"OpenAI response: {response}")
        
        # Return OpenAI response to the user
        return jsonify({"reply": response['choices'][0]['message']['content']})

    except openai.error.OpenAIError as e:
        app.logger.error(f"OpenAI API error: {e}")
        return jsonify({"error": f"OpenAI API error: {e}"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route("/schedule", methods=["GET"])
def get_schedule():
    urls = [
        "https://easy2swim.co.za/age-groups-classes/age-group-2-4-years/2-4-years-age-group-class-registration/",
        "https://easy2swim.co.za/age-groups-classes/age-group-5-7-years/5-7-years-age-group-class-registration/",
        "https://easy2swim.co.za/age-groups-classes/age-group-8-years/8-years-age-group-class-registration/"
    ]

    def to_24h_format(time_str):
        dt = datetime.strptime(time_str.strip(), "%I:%M %p")
        return dt.strftime("%Hh%M")

    def get_abbr_day(day):
        days = {
            "Monday": "Mon", "Tuesday": "Tues", "Wednesday": "Wed",
            "Thursday": "Thurs", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
        }
        return days.get(day, day[:3])

    results = {}

    for url in urls:
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")

            term_info = soup.find(string=re.compile(r"Term Dates|Start Date"))
            date_text = term_info.find_parent().get_text() if term_info else ""
            dates = re.findall(r"(\d{1,2} \w+ \d{4})", date_text)

            if len(dates) >= 2:
                start_date = datetime.strptime(dates[0], "%d %B %Y")
                end_date = datetime.strptime(dates[1], "%d %B %Y")
            else:
                start_date = datetime.today()
                end_date = start_date + timedelta(weeks=10)

            today = datetime.today()
            weeks_left = max(0, ((end_date - today).days // 7) + 1)

            price_match = re.search(r"R(\d{3,5})", page.text)
            total_price = int(price_match.group(1)) if price_match else 1650
            price_per_class = total_price / ((end_date - start_date).days // 7 + 1)
            pro_rata_price = int(round(price_per_class * weeks_left / 5.0) * 5)

            rows = soup.select("table tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue  # Correct use inside a loop

                day_time = cols[0].get_text(strip=True)
                size_text = cols[2].get_text(strip=True)
                class_name = cols[1].get_text(strip=True)  # Assume this is the class name column

                if "/" not in size_text:
                    continue  # Correct use inside a loop
                current, total = map(int, size_text.split("/"))
                if current >= total:
                    continue  # Correct use inside a loop

                if "–" in day_time:
                    day_part, time_part = day_time.split(" ", 1)
                    start_time = time_part.split("–")[0].strip()
                else:
                    day_part, start_time = day_time.split(" ", 1)

                time_24 = to_24h_format(start_time)
                day_abbr = get_abbr_day(day_part)

                register_btn = cols[-1].find("a", href=True)
                if register_btn:
                    link = register_btn["href"]
                    label = f"[{day_abbr} {time_24}]({link}) • {weeks_left} Classes • R{pro_rata_price}"
                    if class_name not in results:
                        results[class_name] = []
                    results[class_name].append({"label": label})

        except Exception as e:
            app.logger.error(f"Error scraping schedule from {url}: {str(e)}")
            results["error"] = f"Error scraping schedule: {e}"

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
