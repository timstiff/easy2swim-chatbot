import openai
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API Key
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your actual API key

# Endpoint for handling the chat
@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()

        user_message = data.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Call OpenAI API to get the chatbot's response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can also use "gpt-4" if available
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant for Easy2Swim Swimming Academy."
            },
            {"role": "user", "content": user_message}],
            max_tokens=150,  # Limit tokens to prevent overuse
            temperature=0.7  # Controls creativity, adjust as needed
        )

        bot_reply = response['choices'][0]['message']['content']
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
