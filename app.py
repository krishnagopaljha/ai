# main.py - Final, simplified version for instant calculations.

import json
import sys
import requests
from asteval import Interpreter
from word2number import w2n

# --- Configuration ---
OLLAMA_API = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3:mini" # must match your pulled model
CALC_TRIGGER = "!calc"

# --- Calculator Logic ---
def safe_calculate(expression: str) -> str:
    """
    Safely evaluates a mathematical expression.
    Returns the result or an error string.
    """
    # Don't try to calculate empty strings
    if not expression.strip():
        return "Error: No expression provided."
    aeval = Interpreter()
    try:
        result = aeval.eval(expression)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except Exception:
        return f"Error: Could not calculate '{expression}'."

# --- LLM Translation Logic (Only used as a fallback) ---
MATH_TRANSLATE_PROMPT = """You are a mathematical expression translator. Convert the user's query into a machine-readable expression. Respond with a single JSON object: {{"expression": "..."}}.

Query: {query}
"""

def translate_to_expression(query: str) -> str | None:
    """
    Uses the LLM to translate natural language into a math expression.
    """
    try:
        processed_query = ' '.join([str(w2n.word_to_num(word)) if word in w2n.american_number_system else word for word in query.split()])
    except ValueError:
        processed_query = query

    prompt = MATH_TRANSLATE_PROMPT.format(query=processed_query)
    payload = { "model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "format": "json", "stream": False }
    
    print("Ollama: (AI fallback) 🧠 Translating...", end="\r", flush=True)
    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=20)
        response.raise_for_status()
        return response.json().get("expression")
    except requests.RequestException as e:
        sys.stdout.write("\r" + " " * 40 + "\r")
        print(f"[ERROR] Could not contact Ollama: {e}", file=sys.stderr)
        return None

# --- Main Application Loop ---
def main():
    print(f"=== Instant Calculator CLI ===")
    print(f"Usage: '{CALC_TRIGGER} 476*34' or '!calc five plus five'")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting...")
            break

        if user_input.strip().lower().startswith(CALC_TRIGGER):
            query = user_input[len(CALC_TRIGGER):].strip()
            
            # --- NEW SIMPLIFIED LOGIC ---
            # 1. First, try to calculate directly.
            direct_result = safe_calculate(query)

            if not direct_result.startswith("Error:"):
                # SUCCESS: The input was a valid formula. Print instantly.
                print(f"Ollama: 🧮 {direct_result}")
            else:
                # FAILURE: The input was not a formula. Use AI as a fallback.
                expression = translate_to_expression(query)
                sys.stdout.write("\r" + " " * 40 + "\r")
                
                if expression:
                    final_result = safe_calculate(expression)
                    print(f"Ollama: 🧮 {final_result}")
                else:
                    print("Ollama: Sorry, I couldn't understand that calculation.")
        else:
            # For simplicity, this version focuses only on the calculator.
            # You can add the stream_chat() function back here if you need general chat.
            print(f"Ollama: Invalid command. Please start with '{CALC_TRIGGER}'.")


if __name__ == "__main__":
    try:
        import requests, asteval
        from word2number import w2n
    except ImportError as e:
        print(f"[FATAL ERROR] Missing library: {e.name}. Please run: pip install requests asteval word2number", file=sys.stderr)
        sys.exit(1)
        
    main()
