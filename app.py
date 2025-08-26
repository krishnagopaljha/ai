from flask import Flask, render_template, request, Response, jsonify, stream_with_context
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# Connection pool for requests
session = requests.Session()
stop_flags = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    # Generate a unique ID for this connection
    connection_id = str(time.time())
    stop_flags[connection_id] = False
    
    def generate():
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "phi3:mini",
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            # Stream directly from Ollama to client with minimal processing
            with session.post(url, json=data, stream=True) as response:
                for line in response.iter_lines():
                    if connection_id in stop_flags and stop_flags[connection_id]:
                        print(f"Generation stopped for connection {connection_id}")
                        break
                    
                    if line:
                        # Convert bytes to string and strip any whitespace
                        line_str = line.decode('utf-8').strip()
                        
                        try:
                            json_response = json.loads(line_str)
                            if 'response' in json_response:
                                yield json_response['response']
                            if json_response.get('done', False):
                                break
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
        except Exception as e:
            yield f"Error: {str(e)}"
        finally:
            # Clean up
            if connection_id in stop_flags:
                del stop_flags[connection_id]
    
    return Response(stream_with_context(generate()), content_type='text/plain')

@app.route('/stop', methods=['POST'])
def stop_generation():
    data = request.get_json()
    connection_id = data.get('connection_id', '')
    
    if connection_id and connection_id in stop_flags:
        stop_flags[connection_id] = True
        return jsonify({"status": "stopped"})
    
    return jsonify({"status": "no active connection"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
