<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Easy2Swim Chatbot</title>
    <style>
        /* Chat Widget Styles */
        #chatWidget {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 90vw;
            max-width: 360px;
            max-height: 75vh;
            border-radius: 16px;
            border: 1px solid #444;
            background: #ffffff;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            padding: 12px;
            display: none;
            flex-direction: column;
            z-index: 9999;
            color: #333;
            overflow: auto;
        }

        #chatHeader {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 6px;
            color: #66ccff;
        }

        #userInput {
            width: 100%;
            min-height: 60px;
            border-radius: 8px;
            border: none;
            padding: 10px;
            background: #f1f1f1;
            color: #333;
            font-size: 14px;
        }

        #userInput::placeholder {
            color: #888;
        }

        #botReply {
            font-size: 14px;
            margin-top: 12px;
            overflow-y: auto;
            max-height: 300px;
            color: #333;
        }

        #chatButton {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            background-color: #0073e6;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 18px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }

        #chatButton:hover {
            background-color: #005bb5;
        }

        #chatWidget button {
            margin-top: 8px;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 8px;
            border: none;
            background: #0073e6;
            color: white;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        #chatWidget button:hover {
            background: #005bb5;
        }

        #chatCloseButton {
            cursor: pointer;
            font-size: 20px;
        }
    </style>
</head>
<body>
    <!-- Chat Window -->
    <div id="chatWidget">
        <div id="chatHeader">
            <div>E2S</div>
            <span id="chatCloseButton" onclick="closeChat()">✖️</span>
        </div>
        <div id="botReply">E2S: Welcome to Easy2Swim. If you are looking for swimming lessons, please give me the age of the swimmer/s and experience or just ask a question.</div>
        <textarea id="userInput" placeholder="Type your question here..." onkeydown="if(event.key === 'Enter'){askBot();}"></textarea>
        <button onclick="askBot()">🚀 Send</button>
    </div>

    <!-- Chat Button -->
    <button id="chatButton" onclick="toggleChat()">💬 Chat to Easy2Swim Assistant</button>

    <script>
        let history = [];
        let manual = `You are the Easy2Swim Assistant. Use the following manual to answer questions:

        Easy2Swim Assistant – AI Agent Overview
        Role & Language Support:
        - You are the friendly and knowledgeable assistant for Easy2Swim Swimming Academy in Gordons Bay, South Africa.
        - Languages Supported: English and Afrikaans
        - Response Style: Clear, helpful, supportive, and professional
        - Use UK English spelling (e.g., metres, programme, floatation)

        IMPORTANT RULE:
        - Before recommending a class for a child, you must ask for and confirm BOTH the child's age AND their swimming ability.
        - Only once you have both pieces of information are you able to safely recommend a class.

        CLASS RECOMMENDATION INSTRUCTIONS:
        - When you recommend a class (e.g., Starfish, Turtle, Stingray, etc.), you must also include:
            1. A list of available class days and times for that specific class.
            2. A registration link using Markdown format like [HERE](https://...) when recommending a class.

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
        `;

        // Toggle chat visibility
        function toggleChat() {
            const chatWidget = document.getElementById('chatWidget');
            const chatButton = document.getElementById('chatButton');

            if (chatWidget.style.display === 'none' || chatWidget.style.display === '') {
                chatWidget.style.display = 'flex';
                chatButton.style.display = 'none'; // Hide button when chat is open
            } else {
                chatWidget.style.display = 'none';
                chatButton.style.display = 'block'; // Show button when chat is closed
            }
        }

        // Ask the bot and send the user message
        function askBot() {
            const userInput = document.getElementById('userInput').value;
            const botReply = document.getElementById('botReply');

            if (userInput.trim() !== "") {
                history.push({ role: "user", content: userInput });

                // Send request to your server (Render API) for bot's response
                fetch('https://easy2swim-chatbot.onrender.com/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userInput,
                        documentation: manual,
                        history: history
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const reply = data.reply;
                    // Update the chat with the bot's response (E2S: message)
                    botReply.innerHTML = `<strong>E2S:</strong> ${reply}`;
                    history.push({ role: "assistant", content: reply });
                })
                .catch(error => console.error("Error:", error));

                document.getElementById('userInput').value = ''; // Clear the input field
            }
        }

        // Close the chat window and clear memory/history
        function closeChat() {
            document.getElementById('chatWidget').style.display = 'none';
            history = [];  // Clear history when the chat window is closed
        }
    </script>
</body>
</html>
