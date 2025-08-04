# app.py
from flask import Flask, render_template, request, Response
import requests
import json
import subprocess
import sys

app = Flask(__name__)

# System prompt for cybersecurity context
CYBERSECURITY_PROMPT = """You are a cybersecurity AI assistant specialized in penetration testing, 
threat analysis, secure coding practices, and vulnerability research. Provide concise technical 
answers with code examples when relevant. Focus on practical security solutions."""

# NEW SIMPLIFIED PROMPT: A simpler, more direct prompt with a strong default.
MATH_ROUTER_PROMPT = """Your default and primary response must be the exact string '[NOT_MATH]'.
The ONLY exception is if the user's query is a direct mathematical calculation that can be solved with a single line of Python (e.g., '15 * 30', '1024/256', '2**10').
In that specific case, and only that case, respond ONLY with the Python code to solve it, wrapped in [PYTHON]...[/PYTHON] tags.
For any other topic, including but not limited to cybersecurity, programming, or general conversation, you must return '[NOT_MATH]'."""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    try:
        router_payload = {
            "model": "codellama:7b-instruct",
            "messages": [
                {"role": "system", "content": MATH_ROUTER_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "options": {"temperature": 0.0}
        }
        
        url = "http://localhost:11434/api/chat"
        router_response = requests.post(url, json=router_payload).json()
        router_content = router_response['message']['content']

        if '[PYTHON]' in router_content and '[/PYTHON]' in router_content:
            code_start = router_content.find('[PYTHON]') + len('[PYTHON]')
            code_end = router_content.find('[/PYTHON]')
            python_code = router_content[code_start:code_end].strip()

            def execute_and_stream():
                try:
                    result = subprocess.run(
                        [sys.executable, '-c', python_code],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        output = result.stdout.strip()
                    else:
                        output = f"Error executing calculation: {result.stderr.strip()}"

                except subprocess.TimeoutExpired:
                    output = "Error: Code execution timed out after 5 seconds."
                except Exception as e:
                    output = f"An error occurred while executing the script: {str(e)}"
                
                response_chunk = {"role": "assistant", "content": output}
                yield f"data: {json.dumps(response_chunk)}\n\n"
                yield "data: [DONE]\n\n"

            return Response(execute_and_stream(), mimetype='text/event-stream')

    except Exception as e:
        print(f"Router failed, falling back to cybersecurity assistant. Error: {e}")

    # --- Fallback to Original Logic ---
    messages = [
        {"role": "system", "content": CYBERSECURITY_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    payload = {
        "model": "codellama:7b-instruct",
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096
        }
    }
    
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
