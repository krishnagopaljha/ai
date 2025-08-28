# core/parser.py
import re
from rapidfuzz import fuzz, process

op_keywords = {
    "+": ["plus", "add", "sum", "+"],
    "-": ["minus", "subtract", "less", "-"],
    "*": ["times", "multiply", "multiplied", "x", "*"],
    "/": ["divide", "divided", "over", "/"],
}

def detect_operator(msg: str, threshold=70):
    words = re.findall(r"[a-z+*/-]+", msg.lower())  # include symbols
    for symbol, keywords in op_keywords.items():
        for w in words:
            match, score, _ = process.extractOne(w, keywords, scorer=fuzz.ratio)
            if score >= threshold:
                return symbol
    return None

def parse_chat_math_local(msg: str):
    # Extract numbers
    nums = re.findall(r"-?\d+(?:\.\d+)?", msg)
    if len(nums) < 2:
        return None

    # Detect operator
    op = detect_operator(msg)
    if not op:
        return None

    a, b = float(nums[0]), float(nums[1])

    # Handle "subtract X from Y"
    if op == "-" and "from" in msg.lower():
        a, b = b, a

    return a, op, b
