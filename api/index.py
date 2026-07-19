from flask import Flask, jsonify, request

app = Flask(__name__)

FAQS = [
    {"question": "what is python", "answer": "Python is a high-level programming language known for its readability and versatility."},
    {"question": "how do i install libraries", "answer": "You can install libraries using pip. For example, run 'pip install flask'."},
    {"question": "what is flask", "answer": "Flask is a lightweight web application framework in Python."},
    {"question": "what is github", "answer": "GitHub is a cloud-based service that helps developers store and manage their code."},
    {"question": "how do i deploy on vercel", "answer": "You can deploy it easily by adding an api folder and putting your script inside."},
    {"question": "what is an ai chatbot", "answer": "An AI chatbot is a software application used to conduct automated text conversations."}
]

# Simple inline HTML interface to completely eliminate template folder paths
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ Chatbot</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, sans-serif; }
        body { background: #f3f4f6; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 440px; height: 85vh; background: white; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); display: flex; flex-direction: column; overflow: hidden; margin: 10px; }
        .chat-header { background: #4f46e5; color: white; padding: 18px; text-align: center; font-weight: 600; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; background: #f9fafb; display: flex; flex-direction: column; gap: 12px; }
        .message { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; }
        .message.user { background: #4f46e5; color: white; align-self: flex-end; border-bottom-right-radius: 0; }
        .message.bot { background: #e5e7eb; color: #1f2937; align-self: flex-start; border-bottom-left-radius: 0; }
        .chat-input-area { display: flex; padding: 14px; background: white; border-top: 1px solid #e5e7eb; }
        .chat-input-area input { flex: 1; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; }
        .chat-input-area button { background: #4f46e5; color: white; border: none; padding: 0 18px; margin-left: 8px; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="chat-header">FAQ Chat Assistant</div>
    <div class="chat-messages" id="chatMessages">
        <div class="message bot">Hello! Ask me anything about Python, Flask, GitHub, or Vercel!</div>
    </div>
    <div class="chat-input-area">
        <input type="text" id="userInput" placeholder="Type a question..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>
<script>
    function appendMessage(text, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    function handleKeyPress(event) { if (event.key === 'Enter') sendMessage(); }
    async function sendMessage() {
        const inputEl = document.getElementById('userInput');
        const text = inputEl.value.trim();
        if (!text) return;
        appendMessage(text, 'user');
        inputEl.value = '';
        try {
            const response = await fetch('/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            appendMessage(data.reply, 'bot');
        } catch (error) {
            appendMessage('Error reaching the assistant.', 'bot');
        }
    }
</script>
</body>
</html>
"""

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if request.method == "POST":
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"reply": "Please ask something!"})
        
        cleaned_input = user_message.lower().strip()
        best_reply = None
        
        for faq in FAQS:
            if faq["question"] in cleaned_input or cleaned_input in faq["question"]:
                best_reply = faq["answer"]
                break
                
        if not best_reply:
            best_reply = "I couldn't find a close match for that question. Try rephrasing!"
            
        return jsonify({"reply": best_reply})
        
    return HTML_INTERFACE
  
