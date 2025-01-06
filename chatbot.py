from flask import Flask, render_template_string, request, jsonify
from ai21 import AI21Client
from ai21.models.chat import ChatMessage, ResponseFormat

app = Flask(__name__)

# Set your API key
api_key = "vYdNnzuI4k1HO5e92DPB2Koz36P6ZKsd"
client = AI21Client(api_key=api_key)

# Function to get OTC recommendations based on symptoms
def get_otc_medicine(symptoms):
    response = client.chat.completions.create(
        model="jamba-1.5-large", 
        messages=[ChatMessage(
            role="user", 
            content=f"Suggest Indian over-the-counter medicines for the following symptoms: {symptoms}"
        )],
        n=1,
        max_tokens=150,
        temperature=0.4,
        response_format=ResponseFormat(type="text")
    )

    # Format the response as a numbered list for better readability
    if hasattr(response, "choices") and len(response.choices) > 0:
        medicine_recommendation = response.choices[0].message.content
        formatted_response = format_recommendation(medicine_recommendation)
        return formatted_response
    else:
        return "Sorry, I couldn't find a recommendation."

# Format the response to make it more readable
def format_recommendation(recommendation):
    """ Format the recommendation as a clean, easy-to-read numbered list """
    lines = recommendation.split("\n")
    formatted_response = ""

    medicine_count = 1
    for line in lines:
        line = line.strip()
        if line.startswith("**"):  # When a new medicine name is found
            formatted_response += f"<br><strong>{medicine_count}. {line}</strong><br>"
            medicine_count += 1
        elif line:  # If the line is not empty, treat it as a description
            formatted_response += f"  - {line}<br>"
    
    return formatted_response.strip()

# HTML Template embedded in the Python file
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTC Medicine Chatbot</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: grey;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }

        .chat-container {
            width: 100%;
            max-width: 600px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .header {
            background-color: #1e1e2f;
            color: white;
            text-align: center;
            padding: 20px 0;
            font-size: 24px;
        }

        .chat-box {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            border-bottom: 1px solid #ddd;
            background-color: #f9f9f9;
            max-height: 500px;
        }

        .message {
            margin: 10px 0;
            padding: 12px;
            border-radius: 8px;
            max-width: 80%;
        }

        .user-message {
            background-color: #cce5ff;
            margin-left: auto;
            margin-right: 0;
            text-align: right;
        }

        .bot-message {
            background-color: #e9ecef;
            margin-left: 0;
            margin-right: auto;
        }

        .input-container {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background-color: #fff;
            border-top: 1px solid #ddd;
        }

        #user-input {
            width: 80%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }

        button {
            padding: 10px 20px;
            border: none;
            background-color: #1e1e2f;
            color: white;
            cursor: pointer;
            border-radius: 5px;
        }

        button:disabled {
            background-color: #ddd;
            cursor: not-allowed;
        }

        .reset-btn {
            background-color: #ff5733;
            margin-top: 20px;
            padding: 10px 20px;
            border-radius: 5px;
        }

        .message strong {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">OTC Medicine Recommendation</div>
        <div class="chat-box" id="chat-box"></div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Enter your symptoms..." onkeyup="if(event.key === 'Enter'){sendMessage()}" />
            <button onclick="sendMessage()">Send</button>
        </div>
        <button class="reset-btn" onclick="resetChat()">Reset</button>
    </div>

    <script>
        let messages = [];

        function sendMessage() {
            const userInput = document.getElementById('user-input').value;
            if (!userInput) return;

            // Add user message
            messages.push({ role: 'user', content: userInput });
            updateChatBox();

            // Call the API to get the bot's response (POST request)
            fetch('/get_medicine', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms: userInput })
            })
            .then(response => response.json())
            .then(data => {
                // Add bot message with formatted points
                messages.push({ role: 'bot', content: data.recommendation });
                updateChatBox();
            });

            // Clear input field
            document.getElementById('user-input').value = '';
        }

        function updateChatBox() {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = '';  // Clear the chat box

            messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', `${msg.role}-message`);
                messageDiv.innerHTML = `<strong>${msg.role === 'user' ? 'You' : 'Bot'}:</strong><br>${msg.content}`;
                chatBox.appendChild(messageDiv);
            });

            // Scroll to the bottom of the chat
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function resetChat() {
            messages = [];
            updateChatBox();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/get_medicine', methods=['POST'])
def get_medicine():
    user_input = request.json.get('symptoms')
    if not user_input:
        return jsonify({'error': 'No symptoms provided'}), 400

    recommendation = get_otc_medicine(user_input)
    return jsonify({'recommendation': recommendation})

if __name__ == '__main__':
    app.run(debug=True)
