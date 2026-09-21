"""
graphing_engine.py
==================
Pure Python & NumPy mathematical graphing engine.
Provides safe AST-based formula parsing, domain validation, discontinuity detection,
and vectorized Cartesian evaluation for 2D function plotting without eval().
"""

import ast
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class PlotFunction:
    """Represents an individual mathematical function plotted on the graph."""
    id: str
    expression: str
    clean_expr: str
    color: str
    line_style: str = "-"  # '-', '--', ':', '-.'
    visible: bool = True
    error: Optional[str] = None


class GraphingEngine:
    """
    Mathematical function parser and evaluation engine for 2D Cartesian graphing.
    Features:
    - Safe AST expression validation (no arbitrary code execution / eval)
    - Vectorized evaluation using NumPy arrays
    - Robust handling of undefined domains (log, sqrt, asin, acos)
    - Asymptote and discontinuity detection (e.g. tan(x), 1/x)
    - Multi-function plotting management
    """

    COLOR_PALETTE = [
        "#38BDF8",  # Sky Blue
        "#34D399",  # Emerald Green
        "#F472B6",  # Pink
        "#FBBF24",  # Amber
        "#A78BFA",  # Violet
        "#FB7185",  # Rose
        "#2DD4BF",  # Teal
        "#818CF8",  # Indigo
        "#F97316",  # Orange
    ]

    ALLOWED_FUNCS = {
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "asin": np.arcsin,
        "acos": np.arccos,
        "atan": np.arctan,
        "sinh": np.sinh,
        "cosh": np.cosh,
        "tanh": np.tanh,
        "sqrt": np.sqrt,
        "cbrt": np.cbrt,
        "log": np.log,
        "ln": np.log,
        "log10": np.log10,
        "log2": np.log2,
        "exp": np.exp,
        "abs": np.abs,
        "floor": np.floor,
        "ceil": np.ceil,
        "sinc": np.sinc,
    }

    ALLOWED_CONSTANTS = {
        "pi": np.pi,
        "e": np.e,
        "tau": 2.0 * np.pi,
    }

    def __init__(self):
        self._functions: List[PlotFunction] = []
        self._next_id: int = 1
        self._color_index: int = 0

    # -------------------------------------------------------------------------
    # Expression Sanitization & Preparation
    # -------------------------------------------------------------------------
    @classmethod
    def clean_expression(cls, expr_str: str) -> str:
        """
        Cleans and standardizes a user-entered function formula.
        Strips 'y =', 'f(x) =', handles implicit multiplication, and unclosed parentheses.
        """
        s = expr_str.strip()
        if not s:
            raise ValueError("Please enter a mathematical expression")

        # Strip 'y =' or 'f(x) =' prefix
        s = re.sub(r"^(?:y\s*=\s*|f\s*\(\s*x\s*\)\s*=\s*)", "", s, flags=re.IGNORECASE).strip()
        if not s:
            raise ValueError("Expression cannot be empty")

        # Replace unicode math symbols
        s = s.replace("×", "*").replace("÷", "/")
        s = s.replace("−", "-")
        s = s.replace("^", "**")
        s = s.replace("π", "pi")

        # Square root symbol: √x -> sqrt(x), √(x) -> sqrt(x)
        s = s.replace("√(", "sqrt(")
        s = re.sub(r"√\s*([a-zA-Z0-9]+)", r"sqrt(\1)", s)

        # Absolute value: |x| -> abs(x)
        s = re.sub(r"\|([^|]+)\|", r"abs(\1)", s)

        # Implicit multiplication:
        # 1. Number before 'x': '2x' -> '2*x', '3.5x' -> '3.5*x'
        s = re.sub(r"\b(\d+(?:\.\d+)?)\s*x\b", r"\1 * x", s)
        # 2. Number before '(': '2(x+1)' -> '2 * (x+1)'
        s = re.sub(r"\b(\d+(?:\.\d+)?)\s*\(", r"\1 * (", s)
        # 2b. 'x' before '(': 'x(x+1)' -> 'x * (x+1)'
        s = re.sub(r"\bx\s*\(", r"x * (", s)
        # 3. ')' before 'x': '(x+1)x' -> '(x+1) * x'
        s = re.sub(r"\)\s*x\b", r") * x", s)
        # 4. ')' before number: '(x+1)2' -> '(x+1) * 2'
        s = re.sub(r"\)\s*(\d+(?:\.\d+)?)", r") * \1", s)
        # 5. ')' before '(': '(x+1)(x-1)' -> '(x+1) * (x-1)'
        s = re.sub(r"\)\s*\(", r") * (", s)
        # 6. 'x' before function or constant: 'x sin(x)' -> 'x * sin(x)', 'x pi' -> 'x * pi'
        s = re.sub(r"\bx\s+([a-zA-Z_]\w*)", r"x * \1", s)
        # 7. Number before named constant (pi, e): '2pi' -> '2 * pi', '3e' -> '3 * e' (protecting scientific notation)
        s = re.sub(r"\b(\d+(?:\.\d+)?)\s*(pi|e(?![+-]?\d))\b", r"\1 * \2", s)
        # 8. Number before function: '2sin(x)' -> '2 * sin(x)'
        func_names = "|".join(cls.ALLOWED_FUNCS.keys())
        s = re.sub(rf"\b(\d+(?:\.\d+)?)\s*({func_names})\b", r"\1 * \2", s)

        # Strip trailing operators: e.g. 'x +' -> 'x'
        s = re.sub(r"[+\-*/]\s*$", "", s)

        # Auto-balance unclosed parentheses
        open_count = s.count("(")
        close_count = s.count(")")
        if open_count > close_count:
            s += ")" * (open_count - close_count)

        return s

    # -------------------------------------------------------------------------
    # AST Validation & Vectorized Evaluation
    # -------------------------------------------------------------------------
    @classmethod
    def validate_ast(cls, expr_str: str) -> ast.AST:
        """
        Parses and strictly validates the AST of the expression.
        Guarantees that only allowed math operations and variables ('x') are present.
        """
        try:
            tree = ast.parse(expr_str, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax: {e.msg}")

        cls._check_node_safety(tree.body)
        return tree.body

    @classmethod
    def _check_node_safety(cls, node: ast.AST) -> None:
        """Recursively inspects AST nodes to disallow any unsafe construct."""
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are supported")
            return

        elif isinstance(node, ast.Name):
            name = node.id
            if name != "x" and name not in cls.ALLOWED_CONSTANTS and name not in cls.ALLOWED_FUNCS:
                raise ValueError(f"Unknown symbol: '{name}'. Use variable 'x' for plotting.")
            return

        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in (ast.UAdd, ast.USub):
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            cls._check_node_safety(node.operand)

        elif isinstance(node, ast.BinOp):
            if type(node.op) not in (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow):
                raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
            cls._check_node_safety(node.left)
            cls._check_node_safety(node.right)

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Dynamic or nested function calls are not allowed")
            func_name = node.func.id
            if func_name not in cls.ALLOWED_FUNCS:
                raise ValueError(f"Unknown function: '{func_name}'")
            if len(node.args) == 0 or len(node.args) > 2:
                raise ValueError(f"Function '{func_name}' expects 1 or 2 arguments")
            for arg in node.args:
                cls._check_node_safety(arg)

        else:
            raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    @classmethod
    def evaluate_node(cls, node: ast.AST, x_vals: np.ndarray) -> np.ndarray:
        """Recursively evaluates an AST node vectorized across a NumPy array."""
        if isinstance(node, ast.Constant):
            return np.full_like(x_vals, float(node.value), dtype=float)

        elif isinstance(node, ast.Name):
            if node.id == "x":
                return x_vals.astype(float)
            elif node.id in cls.ALLOWED_CONSTANTS:
                return np.full_like(x_vals, float(cls.ALLOWED_CONSTANTS[node.id]), dtype=float)
            raise ValueError(f"Unknown symbol: '{node.id}'")

        elif isinstance(node, ast.UnaryOp):
            val = cls.evaluate_node(node.operand, x_vals)
            if isinstance(node.op, ast.USub):
                return -val
            elif isinstance(node.op, ast.UAdd):
                return +val
            raise ValueError("Unsupported unary operator")

        elif isinstance(node, ast.BinOp):
            left = cls.evaluate_node(node.left, x_vals)
            right = cls.evaluate_node(node.right, x_vals)

            with np.errstate(all="ignore"):
                if isinstance(node.op, ast.Add):
                    res = left + right
                elif isinstance(node.op, ast.Sub):
                    res = left - right
                elif isinstance(node.op, ast.Mult):
                    res = left * right
                elif isinstance(node.op, ast.Div):
                    res = np.where(right == 0.0, np.nan, left / right)
                elif isinstance(node.op, ast.FloorDiv):
                    res = np.where(right == 0.0, np.nan, np.floor(left / right))
                elif isinstance(node.op, ast.Mod):
                    res = np.where(right == 0.0, np.nan, left % right)
                elif isinstance(node.op, ast.Pow):
                    res = np.power(left, right)
                    # Mask complex results (e.g. negative base with fractional power)
                    if np.iscomplexobj(res):
                        res = np.where(np.isreal(res), np.real(res), np.nan)
                else:
                    raise ValueError("Unsupported binary operator")

            # Clean infinite values
            res[~np.isfinite(res)] = np.nan
            return res.astype(float)

        elif isinstance(node, ast.Call):
            func_name = node.func.id
            args = [cls.evaluate_node(arg, x_vals) for arg in node.args]

            with np.errstate(all="ignore"):
                if func_name == "log" and len(args) == 2:
                    # Custom base log: log(x, base) = ln(x) / ln(base)
                    res = np.log(args[0]) / np.log(args[1])
                elif len(args) == 1:
                    np_func = cls.ALLOWED_FUNCS[func_name]
                    res = np_func(args[0])
                else:
                    raise ValueError(f"Function '{func_name}' expects 1 argument")

            res[~np.isfinite(res)] = np.nan
            return res.astype(float)

        raise ValueError("Invalid AST node")

    # -------------------------------------------------------------------------
    # Public Evaluation & Discontinuity Filtering
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_function(
        cls, expr_str: str, x_vals: np.ndarray, detect_asymptotes: bool = True
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Evaluates an expression string over an array of x values.
        Returns:
            (y_values, None) on success, or (None, error_message) on failure.
        """
        try:
            clean = cls.clean_expression(expr_str)
            ast_root = cls.validate_ast(clean)
            y_vals = cls.evaluate_node(ast_root, x_vals)

            if detect_asymptotes and len(y_vals) > 1:
                # Detect vertical asymptotes / severe jump discontinuities (e.g. tan(x), 1/x)
                # If adjacent points have huge slope and opposite signs, set to nan to prevent connecting lines
                dy = np.diff(y_vals)
                sign_flip = (y_vals[:-1] * y_vals[1:]) < 0
                threshold = 30.0  # Discontinuity slope threshold
                jump_indices = np.where(sign_flip & (np.abs(dy) > threshold))[0]
                for idx in jump_indices:
                    y_vals[idx] = np.nan

            return y_vals, None

        except Exception as e:
            return None, str(e)

    # -------------------------------------------------------------------------
    # Multi-Function Management
    # -------------------------------------------------------------------------
    def add_function(
        self, expression: str, line_style: str = "-"
    ) -> Tuple[Optional[PlotFunction], Optional[str]]:
        """Validates and adds a new function to the plot list."""
        try:
            clean = self.clean_expression(expression)
            self.validate_ast(clean)

            # Assign color from palette
            color = self.COLOR_PALETTE[self._color_index % len(self.COLOR_PALETTE)]
            self._color_index += 1

            func_id = f"f_{self._next_id}"
            self._next_id += 1

            plot_fn = PlotFunction(
                id=func_id,
                expression=expression.strip(),
                clean_expr=clean,
                color=color,
                line_style=line_style,
                visible=True,
                error=None,
            )
            self._functions.append(plot_fn)
            return plot_fn, None

        except Exception as e:
            return None, str(e)

    def remove_function(self, func_id: str) -> bool:
        """Removes a function by its ID."""
        orig_len = len(self._functions)
        self._functions = [f for f in self._functions if f.id != func_id]
        return len(self._functions) < orig_len

    def clear_functions(self) -> None:
        """Clears all functions from the graph."""
        self._functions.clear()
        self._color_index = 0

    def toggle_visibility(self, func_id: str) -> bool:
        """Toggles the visibility state of a function."""
        for f in self._functions:
            if f.id == func_id:
                f.visible = not f.visible
                return f.visible
        return False

    def set_line_style(self, func_id: str, line_style: str) -> bool:
        """Sets line style ('-', '--', ':', '-.') for a function."""
        for f in self._functions:
            if f.id == func_id:
                f.line_style = line_style
                return True
        return False

    def get_functions(self) -> List[PlotFunction]:
        """Returns list of active plotted functions."""
        return list(self._functions)
