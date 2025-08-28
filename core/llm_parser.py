# core/llm_parser.py
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3:mini"

def parse_chat_math_llm(msg: str):
    system_prompt = (
        "Extract exactly two numbers and one operator from the user message.\n"
        "Allowed operators: +, -, *, /\n"
        "Reply ONLY in JSON like: {\"a\": 10, \"op\": \"*\", \"b\": 20}\n"
        "If not possible, reply with null."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg},
        ],
        "stream": False,
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        r.raise_for_status()
        reply = r.json()["message"]["content"].strip()
        parsed = json.loads(reply)
        if parsed and "a" in parsed and "op" in parsed and "b" in parsed:
            return float(parsed["a"]), parsed["op"], float(parsed["b"])
    except Exception:
        return None

    return None
