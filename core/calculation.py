import subprocess
import sys
import json

def execute_and_stream(python_code):
    """Executes a single-line Python calculation and streams the result."""
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
