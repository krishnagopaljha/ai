# main.py
import json
import requests
from core.calculator import calculate
from core.parser import parse_chat_math_local
from core.llm_parser import parse_chat_math_llm
from core.directory_bruteforcer import extract_target, bruteforce_directories

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3:mini"


def chat_with_phi3(user_msg: str) -> str:
    """Stream reply from Ollama word by word"""
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": user_msg}],
        "stream": True,
    }
    full_reply = []
    with requests.post(OLLAMA_URL, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
                if "message" in data and "content" in data["message"]:
                    text = data["message"]["content"]
                    # print each word separately
                    for word in text.split():
                        print(word, end=" ", flush=True)
                    full_reply.append(text)
            except Exception:
                continue
    print()  # newline after response
    return "".join(full_reply)


def handle_message(user_msg: str) -> str:
    if user_msg.lower().startswith("!chat"):
        parsed = parse_chat_math_local(user_msg)
        if not parsed:
            parsed = parse_chat_math_llm(user_msg)
        if parsed:
            a, op, b = parsed
            try:
                return str(calculate(a, op, b))
            except Exception as e:
                return f"Error: {e}"
        else:
            return "❌ Sorry, I couldn’t understand the math expression."
    elif user_msg.lower().startswith("!word"):
        target = extract_target(user_msg)
        if not target:
            return "❌ Could not find a valid URL or IP address in your request."
        
        found = bruteforce_directories(target)
        
        if found:
            return f"✅ Found accessible paths:\n" + "\n".join(found)
        else:
            return f"ℹ️ No common directories found for {target}."
    else:
        return chat_with_phi3(user_msg)


if __name__ == "__main__":
    print("💬 Chat with Phi3:mini (via Ollama). Use !chat for math. Ctrl+C to quit.")
    try:
        while True:
            user_input = input("> ")
            if user_input.lower().startswith(("!chat", "!word")):
                reply = handle_message(user_input)
                print(reply)
            else:
                chat_with_phi3(user_input)  # Stream reply directly
    except KeyboardInterrupt:
        print("\n👋 Exiting chat.")
