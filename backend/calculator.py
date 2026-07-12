"""Core calculator logic with scientific functions.

Implements a safe expression evaluator using a tokenizer and the
shunting-yard algorithm (no use of eval), so user input never reaches
the Python interpreter directly.
"""

import math
from typing import Callable, Dict

# Maps function names -> (callable, arity)
FUNCTIONS: Dict[str, Callable] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "log": lambda x: math.log10(x),
    "ln": math.log,
    "exp": math.exp,
    "sqrt": math.sqrt,
    # pow takes two args: pow(base, exp)
    "pow": lambda b, e: math.pow(b, e),
}

CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}

# Operator precedence and associativity for binary operators
_BIN_OPS = {
    "+": (2, "L"),
    "-": (2, "L"),
    "*": (3, "L"),
    "/": (3, "L"),
    "^": (4, "R"),
}


class CalculatorError(Exception):
    """Raised when an expression cannot be evaluated."""


def _tokenize(expr: str):
    """Split an expression string into a list of tokens.

    Tokens are tuples of (type, value) where type is one of:
    'num', 'op', 'func', 'const', 'lparen', 'rparen', 'comma'.
    """
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/^(),":
            if c == "+" or c == "-":
                # Detect unary minus/plus when at start or after an operator/LParen
                if not tokens or tokens[-1][0] in ("op", "lparen", "comma", "func"):
                    # Treat as unary: encode with 'u' prefix
                    tokens.append(("op", "u" + c))
                else:
                    tokens.append(("op", c))
            elif c == "(":
                tokens.append(("lparen", c))
            elif c == ")":
                tokens.append(("rparen", c))
            elif c == ",":
                tokens.append(("comma", c))
            else:
                tokens.append(("op", c))
            i += 1
            continue
        if c.isdigit() or c == ".":
            j = i
            seen_dot = False
            while j < n and (expr[j].isdigit() or expr[j] == "."):
                if expr[j] == ".":
                    if seen_dot:
                        raise CalculatorError("Invalid number: multiple decimal points")
                    seen_dot = True
                j += 1
            num_str = expr[i:j]
            if num_str == ".":
                raise CalculatorError("Invalid number: lone decimal point")
            tokens.append(("num", float(num_str)))
            i = j
            continue
        # Identifier: function name or constant
        if c.isalpha():
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            name = expr[i:j].lower()
            i = j
            if name in CONSTANTS:
                tokens.append(("const", CONSTANTS[name]))
            elif name in FUNCTIONS:
                tokens.append(("func", name))
            else:
                raise CalculatorError(f"Unknown identifier: {name}")
            continue
        raise CalculatorError(f"Unexpected character: {c}")

    return tokens


def _apply_unary(op: str, val: float) -> float:
    if op == "u-":
        return -val
    if op == "u+":
        return val
    raise CalculatorError(f"Unknown unary operator: {op}")


def _eval_rpn(rpn):
    """Evaluate a reverse-polish-notation token list."""
    stack = []
    i = 0
    while i < len(rpn):
        typ, val = rpn[i]
        if typ == "num" or typ == "const":
            stack.append(val)
        elif typ == "op":
            if val.startswith("u"):
                if not stack:
                    raise CalculatorError("Malformed expression")
                a = stack.pop()
                stack.append(_apply_unary(val, a))
            else:
                if len(stack) < 2:
                    raise CalculatorError("Malformed expression")
                b = stack.pop()
                a = stack.pop()
                stack.append(_binary_op(val, a, b))
        elif typ == "func":
            fn = FUNCTIONS[val]
            arity = 2 if val == "pow" else 1
            if len(stack) < arity:
                raise CalculatorError(f"Not enough arguments for {val}")
            args = [stack.pop() for _ in range(arity)][::-1]
            try:
                stack.append(fn(*args))
            except (ValueError, ZeroDivisionError, OverflowError) as e:
                raise CalculatorError(f"{val}: {e}")
        else:
            raise CalculatorError("Malformed expression")
        i += 1

    if len(stack) != 1:
        raise CalculatorError("Malformed expression")
    return stack[0]


def _binary_op(op: str, a: float, b: float) -> float:
    try:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise CalculatorError("Division by zero")
            return a / b
        if op == "^":
            return math.pow(a, b)
    except (ValueError, OverflowError) as e:
        raise CalculatorError(f"{op}: {e}")
    raise CalculatorError(f"Unknown operator: {op}")


def _to_rpn(tokens):
    """Convert infix tokens to RPN using the shunting-yard algorithm."""
    output = []
    op_stack = []
    arg_count = {}  # func name -> expected args for pow

    for typ, val in tokens:
        if typ in ("num", "const"):
            output.append((typ, val))
        elif typ == "func":
            op_stack.append((typ, val))
        elif typ == "comma":
            while op_stack and op_stack[-1][0] != "lparen":
                output.append(op_stack.pop())
            if not op_stack:
                raise CalculatorError("Misplaced comma")
        elif typ == "op":
            if val.startswith("u"):
                # Unary operators have highest precedence
                while (
                    op_stack
                    and op_stack[-1][0] == "op"
                    and op_stack[-1][1].startswith("u")
                ):
                    output.append(op_stack.pop())
                op_stack.append((typ, val))
            else:
                prec, assoc = _BIN_OPS[val]
                while op_stack and op_stack[-1][0] == "op":
                    top = op_stack[-1][1]
                    if top.startswith("u"):
                        output.append(op_stack.pop())
                        continue
                    top_prec, top_assoc = _BIN_OPS[top]
                    if (assoc == "L" and prec <= top_prec) or (
                        assoc == "R" and prec < top_prec
                    ):
                        output.append(op_stack.pop())
                    else:
                        break
                op_stack.append((typ, val))
        elif typ == "lparen":
            op_stack.append((typ, val))
        elif typ == "rparen":
            while op_stack and op_stack[-1][0] != "lparen":
                output.append(op_stack.pop())
            if not op_stack:
                raise CalculatorError("Mismatched parentheses")
            op_stack.pop()  # discard lparen
            if op_stack and op_stack[-1][0] == "func":
                output.append(op_stack.pop())

    while op_stack:
        if op_stack[-1][0] in ("lparen", "rparen"):
            raise CalculatorError("Mismatched parentheses")
        output.append(op_stack.pop())

    return output


def evaluate(expression: str) -> float:
    """Evaluate a mathematical expression string.

    Supports basic arithmetic, scientific functions, constants (pi, e),
    parentheses, and operator precedence. Raises CalculatorError on failure.
    """
    if not expression or not expression.strip():
        raise CalculatorError("Empty expression")
    tokens = _tokenize(expression)
    if not tokens:
        raise CalculatorError("Empty expression")
    rpn = _to_rpn(tokens)
    result = _eval_rpn(rpn)
    if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
        raise CalculatorError("Result is not a finite number")
    return result


def available_functions() -> list:
    return sorted(FUNCTIONS.keys())


def available_constants() -> dict:
    return dict(CONSTANTS)
