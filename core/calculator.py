# core/calculator.py
from typing import Literal

Op = Literal["+", "-", "*", "/"]

def calculate(a: float, op: Op, b: float) -> float:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
    raise ValueError(f"Unsupported operator: {op}")
