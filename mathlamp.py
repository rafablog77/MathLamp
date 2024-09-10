from lark import Lark, Transformer, Token
from sys import argv

# The MathLamp grammar
grammar = """
    ?start: statement+

    ?statement: assignment
              | print_statement
              | expression_statement

    ?assignment: variable "=" expression ";"

    print_statement: "print" "(" expression ")" ";"

    ?expression_statement: expression ";"

    ?expression: term
               | expression "+" term -> add
               | expression "-" term -> sub

    ?term: factor
         | term "*" factor -> mul
         | term "/" factor -> div
         | term "%" factor -> mod

    ?factor: number
           | variable
           | "(" expression ")"

    ?variable: identifier

    ?identifier: LETTER (LETTER | DIGIT)*

    ?number: DIGIT+

    LETTER: /[a-zA-Z]/
    DIGIT: /[0-9]+/

    %ignore " "   // Skip spaces
    %ignore "\\t" // Skip tabs
    %ignore "\\n" // Skip newlines
    %ignore "\\r" // Skip carriage returns
"""

# Parser for the MathLamp grammar
parser = Lark(grammar, start='start')

# Interpreter class that walks the parse tree and executes the code
class MathLampInterpreter(Transformer):
    def __init__(self):
        self.variables = {}  # Dictionary to store variables

    # Handle assignment
    def assignment(self, args):
        var_name = str(args[0])  # Convert token to string
        value = self._evaluate(args[1])  # Value of the expression
        self.variables[var_name] = value
        return None  # No need to return anything

    # Handle print statement
    def print_statement(self, args):
        value = self._evaluate(args[0])  # The value to print
        print(value)  # Print the evaluated expression
        return None

    # Handle expression statements
    def expression_statement(self, args):
        return self._evaluate(args[0])

    # Handle basic arithmetic operations
    def add(self, args):
        return self._evaluate(args[0]) + self._evaluate(args[1])

    def sub(self, args):
        return self._evaluate(args[0]) - self._evaluate(args[1])

    def mul(self, args):
        return self._evaluate(args[0]) * self._evaluate(args[1])

    def div(self, args):
        return self._evaluate(args[0]) / self._evaluate(args[1])

    def mod(self, args):
        return self._evaluate(args[0]) % self._evaluate(args[1])

    # Handle numbers and variables
    def number(self, args):
        return int(args[0])  # Convert the number token to an integer

    def variable(self, args):
        var_name = str(args[0])  # Convert token to string
        if var_name in self.variables:
            return self.variables[var_name]
        else:
            raise NameError(f"Variable '{var_name}' not defined")

    # Helper function to evaluate tokens
    def _evaluate(self, value):
        if isinstance(value, Token):  # Check if the value is a Token (e.g., number or identifier)
            if value.type == 'DIGIT':  # If it's a number
                return int(value)
            elif value.type == 'LETTER':  # If it's a variable name
                return self.variable([value])
        elif isinstance(value, int):  # If it's already an integer
            return value
        return value  # Return as is if it's already processed

if "--shell" in argv or "-s" in argv:
    print("Welcome to the MathLamp interactive shell. Press CTRL+C to close the shell")
    while True:
        code = input(">")
        tree = parser.parse(code)
        interpreter = MathLampInterpreter()
        interpreter.transform(tree)
else:
    filepath = argv[1]
    with open(filepath,"r") as f:
        code = f.read()
        tree = parser.parse(code)
        interpreter = MathLampInterpreter()
        interpreter.transform(tree)
