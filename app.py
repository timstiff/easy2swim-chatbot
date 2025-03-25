@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_message = data.get("message")
    documentation = data.get("documentation")
    history = data.get("history", [])

    if not user_message or not documentation:
        return jsonify({"error": "Missing message or documentation"}), 400

    try:
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

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
