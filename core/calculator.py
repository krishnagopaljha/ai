# core/calculator.py

import sys
from asteval import Interpreter

def safe_calculate(expression: str):
    """
    Safely evaluates a mathematical expression using asteval.
    """
    # Create a safe interpreter instance
    aeval = Interpreter()
    
    try:
        # Evaluate the expression
        result = aeval.eval(expression)
        return result
    except Exception as e:
        # Return an error message if evaluation fails
        return f"Error: Could not evaluate '{expression}'. Details: {e}"

if __name__ == "__main__":
    # Ensure that exactly one argument (the expression) is provided
    if len(sys.argv) != 2:
        print("Usage: python calculator.py \"<mathematical_expression>\"")
        sys.exit(1)
        
    input_expression = sys.argv[1]
    output = safe_calculate(input_expression)
    print(output)
