from flask import Flask, jsonify, request
import re

app = Flask(__name__)

# 1. Collect FAQs related to a topic/product (Questions and Answers)
FAQS = [
    # Conversational & Small Talk Intent
    {"intent": "greeting", "keywords": ["hello", "hi", "hey", "greetings", "sup"], "answer": "Hello! I am your FAQ Assistant. How can I help you today?"},
    {"intent": "goodbye", "keywords": ["bye", "goodbye", "exit", "see ya", "later"], "answer": "Goodbye! Have a great day ahead! Let me know if you need anything else later."},
    {"intent": "thanks", "keywords": ["thank", "thanks", "thankyou", "helpful"], "answer": "You're very welcome! I'm happy to help."},
    {"intent": "status", "keywords": ["how", "are", "you", "doing"], "answer": "I'm doing great, thank you for asking! Ready to answer your questions."},
    
    # Technical Project FAQs Intent
    {"intent": "python", "keywords": ["python", "language", "programming"], "answer": "Python is a high-level programming language known for its readability and versatility."},
    {"intent": "libraries", "keywords": ["install", "libraries", "library", "pip", "packages"], "answer": "You can install libraries using pip. For example, run 'pip install flask' in your terminal."},
    {"intent": "flask", "keywords": ["flask", "framework", "microframework"], "answer": "Flask is a lightweight web application framework in Python, perfect for quick serverless setups."},
    {"intent": "github", "keywords": ["github", "git", "repository", "repo"], "answer": "GitHub is a cloud-based service that helps developers store, manage, and track changes to their code."},
    {"intent": "vercel", "keywords": ["deploy", "vercel", "hosting", "deploying"], "answer": "You can deploy it easily by adding an api folder and a vercel.json configuration file to map your application routes."},
    {"intent": "chatbot", "keywords": ["chatbot", "ai", "bot", "assistant"], "answer": "An AI chatbot is a software application used to conduct automated text conversations."}
]

# 2. Preprocess the text (tokenize, clean, lowercase)
def preprocess_text(text):
    # Strip special characters and convert to lower case
    cleaned = re.sub(r'[^a-z0-9\s]', '', text.lower().strip())
    # Tokenize (split into unique words)
    return set(cleaned.split())

# 5. Simple chat UI for user interaction
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
        .chat-header { background: #4f46e5; color: white; padding: 18px; text-align: center; font-weight: 600; font-size: 1.1rem; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; background: #f9fafb; display: flex; flex-direction: column; gap: 12px; }
        .message { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; }
        .message.user { background: #4f46e5; color: white; align-self: flex-end; border-bottom-right-radius: 0; }
        .message.bot { background: #e5e7eb; color: #1f2937; align-self: flex-start; border-bottom-left-radius: 0; }
        .chat-input-area { display: flex; padding: 14px; background: white; border-top: 1px solid #e5e7eb; }
        .chat-input-area input { flex: 1; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; font-size: 0.95rem; }
        .chat-input-area input:focus { border-color: #4f46e5; }
        .chat-input-area button { background: #4f46e5; color: white; border: none; padding: 0 18px; margin-left: 8px; border-radius: 8px; cursor: pointer; font-weight: 500; }
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
        
        # Preprocess input message
        user_words = preprocess_text(user_message)
        
        best_reply = None
        max_similarity = 0.0
        
        # 3. Intent matching / Similarity mapping
        for faq in FAQS:
            faq_keywords = set(faq["keywords"])
            
            # Calculate intersection (matching tokens)
            intersection = user_words.intersection(faq_keywords)
            union = user_words.union(faq_keywords)
            
            if union:
                # Jaccard similarity score metric
                similarity = len(intersection) / len(union)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_reply = faq["answer"]
        
        # 4. Display the best matching answer as a response
        if max_similarity == 0.0 or not best_reply:
            best_reply = "I couldn't find a matching question in my system. Try asking about Python, Flask, Vercel, or GitHub!"
            
        return jsonify({"reply": best_reply})
        
    return HTML_INTERFACE
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
        
        # Clean text and split into individual words
        cleaned_words = re.sub(r'[^a-z0-9\s]', '', user_message.lower().strip()).split()
        
        best_reply = None
        max_matches = 0
        
        # Scan through keywords to find the best contextual match
        for faq in FAQS:
            matches = sum(1 for word in cleaned_words if word in faq["keywords"])
            if matches > max_matches:
                max_matches = matches
                best_reply = faq["answer"]
                
        if max_matches == 0 or not best_reply:
            best_reply = "I couldn't find a matching question in my system. Could you try rephrasing with words like Python, Flask, Vercel, or GitHub?"
            
        return jsonify({"reply": best_reply})
        
    return HTML_INTERFACE
    
