"""
calculator.py
=============
Core calculation engine and state manager for the Scientific Calculator.

Key Design Principles:
1. Complete separation of calculation logic from GUI code.
2. Safe AST (Abstract Syntax Tree) expression parser - avoids unsafe `eval()`.
3. Advanced mathematical operations: Square (x²), Square Root (√x), Power (xʸ),
   Percentage (%), Reciprocal (1/x), Plus/Minus (±), Factorial (x!), Absolute Value (|x|).
4. Graceful error handling: negative square roots, invalid factorials, division by zero,
   overflow limits, and invalid expressions.
"""

import ast
import re
from typing import Dict, Any, Optional

from scientific import ScientificEngine
from history import HistoryManager


class SafeMathEvaluator:
    """
    Safely parses and evaluates mathematical expressions using Python's `ast` module.
    
    This guarantees safety by disallowing arbitrary code execution while preserving
    standard mathematical operator precedence (PEMDAS) and scientific functions.
    """

    # Allowed binary operators
    BINARY_OPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: SafeMathEvaluator._safe_div(a, b),
        ast.FloorDiv: lambda a, b: SafeMathEvaluator._safe_floordiv(a, b),
        ast.Mod: lambda a, b: SafeMathEvaluator._safe_mod(a, b),
        ast.Pow: lambda a, b: ScientificEngine.power(a, b),
    }

    # Allowed unary operators (+, -)
    UNARY_OPS = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    @staticmethod
    def _safe_div(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b

    @staticmethod
    def _safe_floordiv(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a // b

    @staticmethod
    def _safe_mod(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a % b

    def __init__(self, angle_mode: str = "DEG"):
        self.angle_mode = angle_mode

    def _get_functions(self) -> Dict[str, Any]:
        """Maps function names to their implementations in ScientificEngine."""
        mode = self.angle_mode
        return {
            "sin": lambda x: ScientificEngine.sin(x, mode),
            "cos": lambda x: ScientificEngine.cos(x, mode),
            "tan": lambda x: ScientificEngine.tan(x, mode),
            "asin": lambda x: ScientificEngine.asin(x, mode),
            "acos": lambda x: ScientificEngine.acos(x, mode),
            "atan": lambda x: ScientificEngine.atan(x, mode),
            "sinh": ScientificEngine.sinh,
            "cosh": ScientificEngine.cosh,
            "tanh": ScientificEngine.tanh,
            "ln": ScientificEngine.ln,
            "log": ScientificEngine.log10,
            "log10": ScientificEngine.log10,
            "log2": ScientificEngine.log2,
            "exp": ScientificEngine.exp,
            "pow10": ScientificEngine.pow10,
            "sqrt": ScientificEngine.sqrt,
            "cbrt": ScientificEngine.cbrt,
            "sqr": ScientificEngine.square,
            "cube": ScientificEngine.cube,
            "fact": ScientificEngine.factorial,
            "abs": ScientificEngine.abs_val,
            "recip": ScientificEngine.reciprocal,
        }

    def _get_constants(self) -> Dict[str, float]:
        """Allowed mathematical constants."""
        return {
            "pi": ScientificEngine.PI,
            "e": ScientificEngine.E,
            "tau": ScientificEngine.TAU,
        }

    def _evaluate_node(self, node: ast.AST) -> float:
        """Recursively evaluates an AST node."""
        if isinstance(node, ast.Constant):  # Python 3.8+ numbers/constants
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError("Invalid constant type")

        elif isinstance(node, ast.Name):
            constants = self._get_constants()
            if node.id in constants:
                return constants[node.id]
            raise ValueError(f"Unknown symbol: '{node.id}'")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self.UNARY_OPS:
                val = self._evaluate_node(node.operand)
                return self.UNARY_OPS[op_type](val)
            raise ValueError("Unsupported operator")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self.BINARY_OPS:
                left = self._evaluate_node(node.left)
                right = self._evaluate_node(node.right)
                return self.BINARY_OPS[op_type](left, right)
            raise ValueError("Unsupported operator")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function call")
            func_name = node.func.id
            functions = self._get_functions()
            if func_name not in functions:
                raise ValueError(f"Unknown function '{func_name}'")

            args = [self._evaluate_node(arg) for arg in node.args]
            if len(args) != 1:
                raise ValueError(f"Function '{func_name}' expects 1 argument")

            return float(functions[func_name](args[0]))

        raise ValueError("Invalid expression")

    def evaluate(self, expression: str) -> float:
        """Parses and computes the result of the mathematical expression."""
        if not expression or not expression.strip():
            raise ValueError("Invalid expression")

        try:
            parsed = ast.parse(expression.strip(), mode="eval")
        except SyntaxError:
            raise ValueError("Invalid expression")

        return self._evaluate_node(parsed.body)


class CalculatorEngine:
    """
    Main controller for calculator state, user expression management,
    memory storage, and history tracking.
    """

    def __init__(self, history_manager: Optional[HistoryManager] = None):
        self.history = history_manager or HistoryManager()
        self.angle_mode: str = "DEG"  # 'DEG' or 'RAD'
        self.memory_value: float = 0.0
        self.has_memory: bool = False

        # Current calculation states
        self.current_input: str = "0"
        self.previous_expression: str = ""
        self.is_new_calculation: bool = True

    # -------------------------------------------------------------------------
    # Angle Mode (DEG / RAD)
    # -------------------------------------------------------------------------
    def set_angle_mode(self, mode: str) -> None:
        """Sets angle mode to 'DEG' or 'RAD'."""
        if mode.upper() in ("DEG", "RAD"):
            self.angle_mode = mode.upper()

    def toggle_angle_mode(self) -> str:
        """Toggles between DEG and RAD, returning the new mode."""
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        return self.angle_mode

    # -------------------------------------------------------------------------
    # Memory Operations
    # -------------------------------------------------------------------------
    def memory_clear(self) -> None:
        """MC: Clears stored memory."""
        self.memory_value = 0.0
        self.has_memory = False

    def memory_recall(self) -> str:
        """MR: Recalls stored memory value into current input."""
        if self.has_memory:
            self.current_input = self._format_number(self.memory_value)
            self.is_new_calculation = False
        return self.current_input

    def memory_store(self) -> None:
        """MS: Stores current input into memory."""
        try:
            val = float(self.current_input)
            self.memory_value = val
            self.has_memory = True
            self.is_new_calculation = True
        except ValueError:
            pass

    def memory_add(self) -> None:
        """M+: Adds current input to memory."""
        try:
            val = float(self.current_input)
            self.memory_value += val
            self.has_memory = True
            self.is_new_calculation = True
        except ValueError:
            pass

    def memory_subtract(self) -> None:
        """M-: Subtracts current input from memory."""
        try:
            val = float(self.current_input)
            self.memory_value -= val
            self.has_memory = True
            self.is_new_calculation = True
        except ValueError:
            pass

    # -------------------------------------------------------------------------
    # Input Manipulation
    # -------------------------------------------------------------------------
    def append_number(self, num_str: str) -> str:
        """Appends a digit (0-9) to the current input string."""
        if self.is_new_calculation or self.current_input == "0" or "Error" in self.current_input:
            self.current_input = num_str
            self.is_new_calculation = False
        else:
            self.current_input += num_str
        return self.current_input

    def append_decimal(self) -> str:
        """Appends a decimal point, ensuring no duplicate dots in the current token."""
        if self.is_new_calculation or "Error" in self.current_input or self.current_input == "0":
            self.current_input = "0."
            self.is_new_calculation = False
            return self.current_input

        stripped = self.current_input.rstrip()
        # If following an operator or opening parenthesis, append '0.'
        if stripped and stripped[-1] in "+-−×÷/*^(":
            self.current_input = f"{stripped} 0."
            return self.current_input

        # Check if the last number token already has a decimal point
        tokens = re.split(r"[+\-−×÷/*^() ]", self.current_input)
        last_token = tokens[-1] if tokens else ""
        if "." not in last_token:
            self.current_input += "."
        return self.current_input

    def append_operator(self, op: str) -> str:
        """Appends an arithmetic operator (+, -, ×, ÷, ^)."""
        if "Error" in self.current_input:
            self.current_input = "0"

        self.is_new_calculation = False

        # Normalize operator symbol
        if op in ("*", "×"):
            op_symbol = "×"
        elif op in ("/", "÷"):
            op_symbol = "÷"
        elif op in ("-", "−"):
            op_symbol = "−"
        else:
            op_symbol = "+" if op == "+" else op

        stripped = self.current_input.rstrip()

        # If user starts with minus on initial 0, treat as negative sign
        if self.current_input == "0" and op_symbol in ("-", "−"):
            self.current_input = "−"
            return self.current_input

        # If previous character is an operator or open bracket and op is minus,
        # allow unary minus e.g. '5 × −' or '(−'
        if op_symbol in ("-", "−") and stripped and stripped[-1] in "×÷/*^(":
            self.current_input = f"{stripped} −"
            return self.current_input

        # If current input already ends with an operator, replace it
        if stripped and stripped[-1] in "+-−×÷^":
            self.current_input = stripped[:-1].rstrip() + f" {op_symbol} "
        else:
            self.current_input = f"{self.current_input} {op_symbol} "

        return self.current_input

    def append_bracket(self, bracket: str) -> str:
        """Appends an open '(' or close ')' parenthesis."""
        if self.is_new_calculation or self.current_input == "0" or "Error" in self.current_input:
            self.current_input = bracket
            self.is_new_calculation = False
        else:
            self.current_input += bracket
        return self.current_input

    def append_constant(self, constant_name: str) -> str:
        """Inserts a mathematical constant (π, e)."""
        symbol = "π" if constant_name in ("pi", "π") else "e"
        if self.is_new_calculation or self.current_input == "0" or "Error" in self.current_input:
            self.current_input = symbol
            self.is_new_calculation = False
        else:
            # If following a digit or closing parenthesis, add implicit multiplication
            if self.current_input[-1].isdigit() or self.current_input[-1] == ")":
                self.current_input += f" × {symbol}"
            else:
                self.current_input += symbol
        return self.current_input

    def apply_function(self, func_name: str) -> str:
        """
        Inserts a function call like sin(, cos(, sqrt(, ln(, etc.
        Starts a new function call or appends it to the current formula.
        """
        if "Error" in self.current_input or self.is_new_calculation or self.current_input == "0":
            self.current_input = f"{func_name}("
            self.is_new_calculation = False
            return self.current_input

        stripped = self.current_input.rstrip()
        if stripped and (stripped[-1].isdigit() or stripped[-1] in ")πe"):
            self.current_input = f"{stripped} × {func_name}("
        else:
            self.current_input = f"{stripped}{func_name}("

        self.is_new_calculation = False
        return self.current_input

    def apply_unary_operation(self, op: str) -> str:
        """
        Applies immediate unary operation like square (x²), square root (√x),
        reciprocal (1/x), cube (x³), factorial (n!), percentage (%), or absolute value (|x|).
        """
        if "Error" in self.current_input:
            return self.current_input

        # Try to evaluate the current input first if it's an expression
        try:
            val = self.evaluate_expression(self.current_input)
        except Exception:
            try:
                val = float(self.current_input)
            except ValueError:
                self.current_input = "Error: Invalid expression"
                self.is_new_calculation = True
                return self.current_input

        try:
            if op == "sqr":
                res = ScientificEngine.square(val)
                label = f"sqr({self._format_number(val)})"
            elif op == "sqrt":
                res = ScientificEngine.sqrt(val)
                label = f"√({self._format_number(val)})"
            elif op == "cube":
                res = ScientificEngine.cube(val)
                label = f"cube({self._format_number(val)})"
            elif op == "recip":
                res = ScientificEngine.reciprocal(val)
                label = f"1/({self._format_number(val)})"
            elif op == "fact":
                res = float(ScientificEngine.factorial(val))
                label = f"{self._format_number(val)}!"
            elif op == "percent":
                res = ScientificEngine.percentage(val)
                label = f"{self._format_number(val)}%"
            elif op == "abs":
                res = ScientificEngine.abs_val(val)
                label = f"|{self._format_number(val)}|"
            elif op == "exp":
                res = ScientificEngine.exp(val)
                label = f"exp({self._format_number(val)})"
            else:
                raise ValueError("Invalid operation")

            formatted = self._format_number(res)
            self.previous_expression = label
            self.history.add(self.previous_expression, formatted)
            self.current_input = formatted
            self.is_new_calculation = True
            return self.current_input

        except ZeroDivisionError:
            self.current_input = "Error: Division by zero"
            self.is_new_calculation = True
            return self.current_input
        except OverflowError:
            self.current_input = "Error: Result too large"
            self.is_new_calculation = True
            return self.current_input
        except ValueError as err:
            msg = str(err)
            if not msg.startswith("Error"):
                msg = f"Error: {msg}"
            self.current_input = msg
            self.is_new_calculation = True
            return self.current_input

    def toggle_sign(self) -> str:
        """Toggles the sign (+/-) of the current number or trailing operand."""
        if "Error" in self.current_input or self.current_input == "0":
            return self.current_input

        # Check if the whole string is a simple number
        try:
            val = float(self.current_input)
            if val.is_integer():
                self.current_input = str(-int(val))
            else:
                self.current_input = str(-val)
            return self.current_input
        except ValueError:
            pass

        # Check if expression ends with (-num)
        neg_match = re.search(r"\(-(\d+(?:\.\d+)?)\)$", self.current_input)
        if neg_match:
            start, _ = neg_match.span()
            num = neg_match.group(1)
            self.current_input = self.current_input[:start] + num
            return self.current_input

        # Check if expression ends with a positive number
        pos_match = re.search(r"(\d+(?:\.\d+)?)$", self.current_input)
        if pos_match:
            start, _ = pos_match.span()
            num = pos_match.group(1)
            self.current_input = self.current_input[:start] + f"(-{num})"
            return self.current_input

        # Otherwise wrap/unwrap entire expression
        if self.current_input.startswith("-(") and self.current_input.endswith(")"):
            self.current_input = self.current_input[2:-1]
        else:
            self.current_input = f"-({self.current_input})"
        return self.current_input

    def backspace(self) -> str:
        """Removes the last character from current input."""
        if "Error" in self.current_input:
            self.current_input = "0"
            self.is_new_calculation = True
            return self.current_input

        self.is_new_calculation = False
        self.current_input = self.current_input.rstrip()
        if len(self.current_input) <= 1:
            self.current_input = "0"
            self.is_new_calculation = True
        else:
            self.current_input = self.current_input[:-1].rstrip()
            if not self.current_input:
                self.current_input = "0"
                self.is_new_calculation = True

        return self.current_input

    def clear(self) -> str:
        """C: Clears current input line."""
        self.current_input = "0"
        self.is_new_calculation = True
        return self.current_input

    def all_clear(self) -> str:
        """AC: Clears current input and previous expression."""
        self.current_input = "0"
        self.previous_expression = ""
        self.is_new_calculation = True
        return self.current_input

    # -------------------------------------------------------------------------
    # Evaluation & Preprocessing
    # -------------------------------------------------------------------------
    def _sanitize_for_evaluation(self, expr_str: str) -> str:
        """
        Converts human-readable calculator expression into valid Python AST syntax.
        Handles unicode symbols, absolute values |x|, percentages, factorials,
        implicit multiplication, and unclosed parentheses.
        """
        s = expr_str.strip()

        # Replace unicode symbols with standard Python math operators
        s = s.replace("×", "*").replace("÷", "/")
        s = s.replace("−", "-")
        s = s.replace("^", "**")
        s = s.replace("π", "pi")

        # Convert absolute value: e.g. |-5| -> abs(-5)
        s = re.sub(r"\|([^|]+)\|", r"abs(\1)", s)

        # Convert percentage: e.g. '50%' -> '(50/100)'
        s = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", s)

        # Convert factorial: e.g. '5!' -> 'fact(5)'
        s = re.sub(r"(\d+(?:\.\d+)?)\s*\!", r"fact(\1)", s)

        # Convert square root: '√25' -> 'sqrt(25)', '√(25)' -> 'sqrt(25)'
        s = s.replace("√(", "sqrt(")
        s = re.sub(r"√\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", s)

        # Implicit multiplication:
        # 1. Number before '(': '5(2+3)' -> '5 * (2+3)' (using \b to avoid matching log10)
        s = re.sub(r"\b(\d+(?:\.\d+)?)\s*\(", r"\1 * (", s)
        # 2. ')' before number: '(2+3)5' -> '(2+3) * 5'
        s = re.sub(r"\)\s*(\d+(?:\.\d+)?)", r") * \1", s)
        # 3. ')' before '(': '(2+3)(4+1)' -> '(2+3) * (4+1)'
        s = re.sub(r"\)\s*\(", r") * (", s)
        # 4. Number before constant: '2pi' -> '2 * pi', '3e' -> '3 * e'
        s = re.sub(r"\b(\d+(?:\.\d+)?)\s*(pi|e)\b", r"\1 * \2", s)
        # 5. Constant before '(': 'pi(2)' -> 'pi * (2)'
        s = re.sub(r"\b(pi|e)\s*\(", r"\1 * (", s)
        # 6. ')' before constant: '(2)pi' -> '(2) * pi'
        s = re.sub(r"\)\s*(pi|e)\b", r") * \1", s)

        # Strip trailing operators: '5 +' -> '5'
        s = re.sub(r"[+\-*/]\s*$", "", s)

        # Automatically balance unclosed open parentheses
        open_count = s.count("(")
        close_count = s.count(")")
        if open_count > close_count:
            s += ")" * (open_count - close_count)

        return s

    def evaluate_expression(self, expression_str: str) -> float:
        """Evaluates an expression string safely using SafeMathEvaluator."""
        sanitized = self._sanitize_for_evaluation(expression_str)
        evaluator = SafeMathEvaluator(angle_mode=self.angle_mode)
        return evaluator.evaluate(sanitized)

    def calculate(self) -> str:
        """
        Evaluates current input, updates history, and sets previous expression.
        Returns the formatted result string or clear error message.
        """
        if "Error" in self.current_input:
            return self.current_input

        original_expr = self.current_input.strip()
        if not original_expr:
            return "0"

        try:
            result_val = self.evaluate_expression(original_expr)
            formatted = self._format_number(result_val)

            # Update calculator display state
            self.previous_expression = f"{original_expr} ="
            self.history.add(original_expr, formatted)
            self.current_input = formatted
            self.is_new_calculation = True
            return self.current_input

        except ZeroDivisionError:
            self.previous_expression = f"{original_expr} ="
            self.current_input = "Error: Division by zero"
            self.is_new_calculation = True
            return self.current_input

        except OverflowError:
            self.previous_expression = f"{original_expr} ="
            self.current_input = "Error: Result too large"
            self.is_new_calculation = True
            return self.current_input

        except ValueError as ve:
            self.previous_expression = f"{original_expr} ="
            msg = str(ve)
            if not msg.startswith("Error"):
                msg = f"Error: {msg}"
            self.current_input = msg
            self.is_new_calculation = True
            return self.current_input

        except Exception:
            self.previous_expression = f"{original_expr} ="
            self.current_input = "Error: Invalid expression"
            self.is_new_calculation = True
            return self.current_input

    def _format_number(self, value: float) -> str:
        """Formats numbers cleanly, stripping unnecessary trailing zeros and formatting floats."""
        # Check integer
        if abs(value - round(value)) < 1e-12:
            return str(int(round(value)))

        # Very large or tiny numbers: use scientific notation
        if abs(value) >= 1e13 or (0 < abs(value) < 1e-6):
            return f"{value:.6e}".replace("e+0", "e+").replace("e-0", "e-")

        # Standard float rounding to 10 decimal places and strip trailing zeros
        rounded = round(value, 10)
        formatted = f"{rounded:.10f}".rstrip("0").rstrip(".")
        return formatted
