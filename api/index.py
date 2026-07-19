from flask import Flask, jsonify, request
import re

app = Flask(__name__)

# 1. FAQ Data Collection
FAQS = [
    {"intent": "greeting", "keywords": ["hello", "hi", "hey", "greetings", "sup"], "answer": "Hello! I am your FAQ Assistant. How can I help you today?"},
    {"intent": "goodbye", "keywords": ["bye", "goodbye", "exit", "see ya", "later"], "answer": "Goodbye! Have a great day ahead!"},
    {"intent": "thanks", "keywords": ["thank", "thanks", "thankyou"], "answer": "You're very welcome!"},
    {"intent": "status", "keywords": ["how", "are", "you"], "answer": "I'm doing great, thank you! Ready to answer your questions."},
    {"intent": "python", "keywords": ["python", "language"], "answer": "Python is a high-level programming language known for readability."},
    {"intent": "libraries", "keywords": ["install", "libraries", "pip"], "answer": "You can install libraries using pip. For example: pip install flask."},
    {"intent": "flask", "keywords": ["flask", "framework"], "answer": "Flask is a lightweight web application framework in Python."},
    {"intent": "github", "keywords": ["github", "git"], "answer": "GitHub is a cloud service that helps developers store and manage code."},
    {"intent": "vercel", "keywords": ["deploy", "vercel"], "answer": "You can deploy it easily by adding an api folder and a vercel.json file."},
    {"intent": "chatbot", "keywords": ["chatbot", "ai"], "answer": "An AI chatbot is a software application used to conduct text conversations."}
]

def preprocess_text(text):
    cleaned = re.sub(r'[^a-z0-9\s]', '', text.lower().strip())
    return set(cleaned.split())

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
        .message { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; }
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

# Vercel reads this route pattern explicitly as the default handler
@app.route("/", methods=["GET", "POST"])
@app.route("/api", methods=["GET", "POST"])
def handler():
    if request.method == "POST":
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"reply": "Please ask something!"})
        
        user_words = preprocess_text(user_message)
        best_reply = None
        max_similarity = 0.0
        
        for faq in FAQS:
            faq_keywords = set(faq["keywords"])
            intersection = user_words.intersection(faq_keywords)
            union = user_words.union(faq_keywords)
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_reply = faq["answer"]
        
        if max_similarity == 0.0 or not best_reply:
            best_reply = "I couldn't find a matching question. Try asking about Python, Flask, Vercel, or GitHub!"
            
        return jsonify({"reply": best_reply})
        
    return HTML_INTERFACE
    
