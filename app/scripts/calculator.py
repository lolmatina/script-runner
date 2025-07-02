#!/usr/bin/env python3
"""
Enhanced Calculator Script with Multiple Modes
Supports basic arithmetic, advanced functions, and expression evaluation
"""

import sys
import math
import operator

# Dictionary of mathematical operations
OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '**': operator.pow,
    '%': operator.mod,
    '//': operator.floordiv
}

# Dictionary of mathematical functions
FUNCTIONS = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    'abs': abs,
    'ceil': math.ceil,
    'floor': math.floor,
    'round': round
}

def show_help():
    """Display comprehensive help information."""
    print("CALCULATOR SCRIPT HELP")
    print("=" * 25)
    print()
    print("DESCRIPTION:")
    print("   Advanced calculator supporting multiple operation modes")
    print()
    print("USAGE MODES:")
    print()
    print("1. BASIC ARITHMETIC:")
    print("   python calculator.py <number1> <operator> <number2>")
    print("   Example: python calculator.py 10 + 5")
    print("   Operators: +, -, *, /, **, %, //")
    print()
    print("2. EXPRESSION EVALUATION:")
    print("   python calculator.py --eval \"<expression>\"")
    print("   Example: python calculator.py --eval \"(10 + 5) * 2 - 3\"")
    print()
    print("3. FUNCTION CALLS:")
    print("   python calculator.py --func <function> <number>")
    print("   Example: python calculator.py --func sqrt 16")
    print("   Functions: sqrt, sin, cos, tan, log, log10, exp, abs, ceil, floor, round")
    print()
    print("4. ADVANCED CALCULATION:")
    print("   python calculator.py --advanced <num1> <op> <num2> [precision]")
    print("   Example: python calculator.py --advanced 22 / 7 4")
    print()
    print("OPTIONS:")
    print("   --help, -h     Show this help message")
    print("   --version      Show version information")
    print()
    print("EXAMPLES:")
    print("   python calculator.py 15 + 25")
    print("   python calculator.py 8 ** 2")
    print("   python calculator.py --eval \"2 * (3 + 4)\"")
    print("   python calculator.py --func sin 1.57")
    print("   python calculator.py --advanced 355 / 113 10")

def perform_basic_calculation(num1, op, num2):
    """Perform basic arithmetic operations."""
    try:
        if op not in OPERATORS:
            return None, f"Unsupported operator: {op}"
        
        if op == '/' and num2 == 0:
            return None, "Division by zero is not allowed"
        
        if op == '%' and num2 == 0:
            return None, "Modulo by zero is not allowed"
        
        result = OPERATORS[op](num1, num2)
        return result, None
        
    except Exception as e:
        return None, str(e)

def perform_advanced_calculation(num1, op, num2, precision=6):
    """Perform advanced calculation with specified precision."""
    try:
        result, error = perform_basic_calculation(num1, op, num2)
        if error:
            return None, error
        
        # Round to specified precision
        if isinstance(result, float):
            result = round(result, precision)
        
        return result, None
        
    except Exception as e:
        return None, str(e)

def evaluate_expression(expression):
    """Safely evaluate mathematical expressions."""
    try:
        # Remove any dangerous characters/functions for security
        forbidden = ['import', 'exec', 'eval', '__', 'open', 'file']
        expr_lower = expression.lower()
        
        for forbidden_item in forbidden:
            if forbidden_item in expr_lower:
                return None, f"Forbidden operation detected: {forbidden_item}"
        
        # Replace mathematical function names with math module equivalents
        safe_expression = expression.replace('^', '**')  # Allow ^ for power
        
        # Add math functions to the allowed names
        allowed_names = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "pow": pow,
            "max": max,
            "min": min,
            "sum": sum,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "ceil": math.ceil,
            "floor": math.floor
        }
        
        result = eval(safe_expression, allowed_names)
        return result, None
        
    except ZeroDivisionError:
        return None, "Division by zero"
    except ValueError as e:
        return None, f"Value error: {e}"
    except SyntaxError as e:
        return None, f"Syntax error in expression: {e}"
    except Exception as e:
        return None, f"Error evaluating expression: {e}"

def perform_function_calculation(function_name, number):
    """Perform mathematical function calculations."""
    try:
        if function_name not in FUNCTIONS:
            available = ', '.join(FUNCTIONS.keys())
            return None, f"Unknown function: {function_name}. Available: {available}"
        
        # Special handling for certain functions
        if function_name in ['log', 'log10'] and number <= 0:
            return None, f"Logarithm undefined for non-positive numbers: {number}"
        
        if function_name == 'sqrt' and number < 0:
            return None, f"Square root undefined for negative numbers: {number}"
        
        func = FUNCTIONS[function_name]
        result = func(number)
        
        return result, None
        
    except Exception as e:
        return None, str(e)

def main():
    """Main calculator function."""
    args = sys.argv[1:]  # Remove script name
    
    if not args:
        print("No arguments provided!")
        print("Use --help for usage information")
        return
    
    # Handle help and version
    if args[0] in ['--help', '-h', 'help']:
        show_help()
        return
    
    if args[0] == '--version':
        print("Calculator Script v2.0")
        print("Enhanced mathematical calculator with multiple modes")
        return
    
    # Mode 1: Basic arithmetic (3 arguments)
    if len(args) == 3 and args[1] in OPERATORS:
        try:
            num1 = float(args[0])
            op = args[1]
            num2 = float(args[2])
            
            print("CALCULATION DETAILS:")
            print(f"   Operation: {num1} {op} {num2}")
            print(f"   Mode: Basic Arithmetic")
            
            result, error = perform_basic_calculation(num1, op, num2)
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Result: {result}")
                
                # Additional information for certain operations
                if op == '/':
                    print(f"   Quotient: {result}")
                    if num2 != 0:
                        remainder = num1 % num2
                        print(f"   Remainder: {remainder}")
                elif op == '**':
                    print(f"   Power calculation: {num1} raised to {num2}")
                elif op == '//':
                    print(f"   Floor division result: {result}")
                    
        except ValueError as e:
            print(f"Unexpected error: {e}")
            return
    
    # Mode 2: Expression evaluation
    elif len(args) >= 2 and args[0] == '--eval':
        if len(args) < 2:
            print("No expression provided after --eval")
            return
        
        # Join all arguments after --eval to handle expressions with spaces
        expression = ' '.join(args[1:])
        
        print("EXPRESSION EVALUATION:")
        print(f"   Expression: {expression}")
        print(f"   Mode: Expression Evaluation")
        
        result, error = evaluate_expression(expression)
        
        if error:
            print(f"Error: {error}")
        else:
            print(f"Result: {result}")
            
    # Mode 3: Function calculation
    elif len(args) >= 3 and args[0] == '--func':
        try:
            function = args[1]
            number = float(args[2])
            
            print("FUNCTION CALCULATION:")
            print(f"   Function: {function}({number})")
            print(f"   Mode: Function Call")
            
            result, error = perform_function_calculation(function, number)
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Result: {result}")
                print(f"Function: {function}, Input: {number}, Output: {result}")
                
        except ValueError as e:
            print(f"Error: {error}")
        except IndexError:
            print("Invalid number of arguments!")
            print("Use --help for usage information")
            return
    
    # Mode 4: Advanced calculation with precision
    elif len(args) >= 4 and args[0] == '--advanced':
        try:
            num1 = float(args[1])
            op = args[2]
            num2 = float(args[3])
            precision = int(args[4]) if len(args) > 4 else 6
            
            print("ADVANCED CALCULATION:")
            print(f"   Operation: {num1} {op} {num2}")
            print(f"   Precision: {precision} decimal places")
            print(f"   Mode: Advanced")
            
            result, error = perform_advanced_calculation(num1, op, num2, precision)
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Result: {result}")
                
        except ValueError as e:
            print(f"Error: {error}")
    
    else:
        print("Invalid arguments!")
        print("Use --help for usage information")
        return
    
    print("\nCALCULATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCalculation interrupted by user")
        sys.exit(0)
    except ValueError as e:
        print(f"Invalid number format: {e}")
        print("Make sure all numeric arguments are valid numbers")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1) 