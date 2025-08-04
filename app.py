# app.py
from flask import Flask, render_template, request, jsonify, Response
import requests
import json

app = Flask(__name__)

# System prompt for cybersecurity context
CYBERSECURITY_PROMPT = """You are a cybersecurity AI assistant specialized in penetration testing, 
threat analysis, secure coding practices, and vulnerability research. Provide concise technical 
answers with code examples when relevant. Focus on practical security solutions."""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Prepare messages with cybersecurity context
    messages = [
        {"role": "system", "content": CYBERSECURITY_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    # Ollama API payload
    payload = {
        "model": "codellama:7b-instruct",
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096
        }
    }
    
    # Stream response from Ollama
    def generate():
        url = "http://localhost:11434/api/chat"
        with requests.post(url, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if not chunk.get("done", False):
                        yield f"data: {json.dumps(chunk['message'])}\n\n"
                    else:
                        yield "data: [DONE]\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
