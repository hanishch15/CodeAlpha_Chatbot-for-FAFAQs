from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Pre-defined FAQ Knowledge base
FAQS = [
    {"question": "what is python", "answer": "Python is a high-level programming language known for its readability and versatility."},
    {"question": "how do i install libraries", "answer": "You can install libraries using pip. For example, run 'pip install flask' in your terminal."},
    {"question": "what is flask", "answer": "Flask is a lightweight web application framework in Python, perfect for quick setups."},
    {"question": "what is github", "answer": "GitHub is a cloud-based service that helps developers store, manage, and track changes to their code."},
    {"question": "how do i deploy on vercel", "answer": "You can deploy it easily by adding a vercel.json configuration file to map your application routes."},
    {"question": "what is an ai chatbot", "answer": "An AI chatbot is a software application used to conduct automated text conversations."}
]

def clean_text(text):
    # Standardize input to lower case and strip special characters
    return re.sub(r'[^a-z0-9\s]', '', text.lower().strip())

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Please ask something!"})
    
    cleaned_input = clean_text(user_message)
    best_reply = None
    
    # Check for keywords matching our FAQ dataset
    for faq in FAQS:
        if faq["question"] in cleaned_input or cleaned_input in faq["question"]:
            best_reply = faq["answer"]
            break
            
    if not best_reply:
        best_reply = "I'm sorry, I couldn't find a close match for your question. Could you try rephrasing it?"
        
    return jsonify({"reply": best_reply})

if __name__ == "__main__":
    app.run(debug=True)
  
