"""
scientific.py
=============
Scientific calculation module powered strictly by Python's built-in `math` library.

This module provides pure mathematical functions isolated from any user interface.
It is designed to be clean, robust, and easy for beginners to read and understand.
"""

import math
from typing import Union

Number = Union[int, float]


class ScientificEngine:
    """
    Provides scientific mathematical operations with support for Degree (DEG)
    and Radian (RAD) angle modes.
    """

    # Mathematical constants
    PI = math.pi
    E = math.e
    TAU = math.tau

    @staticmethod
    def _to_radians(angle: Number, mode: str = "DEG") -> float:
        """Converts an angle to radians if mode is DEG, otherwise assumes RAD."""
        if mode.upper() == "DEG":
            return math.radians(angle)
        return float(angle)

    @staticmethod
    def _from_radians(angle_rad: float, mode: str = "DEG") -> float:
        """Converts radians to degrees if mode is DEG, otherwise leaves as RAD."""
        if mode.upper() == "DEG":
            return math.degrees(angle_rad)
        return angle_rad

    # -------------------------------------------------------------------------
    # Trigonometric Functions
    # -------------------------------------------------------------------------
    @classmethod
    def sin(cls, x: Number, mode: str = "DEG") -> float:
        """Calculates sine of x in DEG or RAD mode."""
        rad = cls._to_radians(x, mode)
        # Handle precision around multiples of pi (e.g., sin(180) should be 0, not 1.22e-16)
        val = math.sin(rad)
        return 0.0 if abs(val) < 1e-15 else val

    @classmethod
    def cos(cls, x: Number, mode: str = "DEG") -> float:
        """Calculates cosine of x in DEG or RAD mode."""
        rad = cls._to_radians(x, mode)
        val = math.cos(rad)
        return 0.0 if abs(val) < 1e-15 else val

    @classmethod
    def tan(cls, x: Number, mode: str = "DEG") -> float:
        """Calculates tangent of x in DEG or RAD mode."""
        rad = cls._to_radians(x, mode)
        c = math.cos(rad)
        if abs(c) < 1e-15:
            raise ValueError("Tangent undefined (division by zero at 90° + k*180°)")
        val = math.tan(rad)
        return 0.0 if abs(val) < 1e-15 else val

    @classmethod
    def asin(cls, x: Number, mode: str = "DEG") -> float:
        """Calculates arcsine (inverse sine) in DEG or RAD."""
        if not -1.0 <= x <= 1.0:
            raise ValueError("Arcsin domain error: input must be in [-1, 1]")
        return cls._from_radians(math.asin(x), mode)

    @classmethod
    def acos(cls, x: Number, mode: str = "DEG") -> float:
        """Calculates arccosine (inverse cosine) in DEG or RAD."""
        if not -1.0 <= x <= 1.0:
            raise ValueError("Arccos domain error: input must be in [-1, 1]")
        return cls._from_radians(math.acos(x), mode)

    @classmethod
    def atan(cls, x: Number, mode: str = "DEG") -> float:
        """Calculates arctangent (inverse tangent) in DEG or RAD."""
        return cls._from_radians(math.atan(x), mode)

    # -------------------------------------------------------------------------
    # Hyperbolic Functions
    # -------------------------------------------------------------------------
    @staticmethod
    def sinh(x: Number) -> float:
        """Hyperbolic sine."""
        return math.sinh(x)

    @staticmethod
    def cosh(x: Number) -> float:
        """Hyperbolic cosine."""
        return math.cosh(x)

    @staticmethod
    def tanh(x: Number) -> float:
        """Hyperbolic tangent."""
        return math.tanh(x)

    # -------------------------------------------------------------------------
    # Logarithmic & Exponential Functions
    # -------------------------------------------------------------------------
    @staticmethod
    def ln(x: Number) -> float:
        """Natural logarithm (base e)."""
        if x <= 0:
            raise ValueError("Logarithm domain error: x must be > 0")
        return math.log(x)

    @staticmethod
    def log10(x: Number) -> float:
        """Logarithm base 10."""
        if x <= 0:
            raise ValueError("Logarithm domain error: x must be > 0")
        return math.log10(x)

    @staticmethod
    def log2(x: Number) -> float:
        """Logarithm base 2."""
        if x <= 0:
            raise ValueError("Logarithm domain error: x must be > 0")
        return math.log2(x)

    @staticmethod
    def exp(x: Number) -> float:
        """Calculates e^x."""
        return math.exp(x)

    @staticmethod
    def pow10(x: Number) -> float:
        """Calculates 10^x."""
        return math.pow(10, x)

    # -------------------------------------------------------------------------
    # Powers, Roots & Arithmetic Utilities
    # -------------------------------------------------------------------------
    @staticmethod
    def square(x: Number) -> float:
        """Calculates x²."""
        return float(x ** 2)

    @staticmethod
    def cube(x: Number) -> float:
        """Calculates x³."""
        return float(x ** 3)

    @staticmethod
    def power(base: Number, exponent: Number) -> float:
        """Calculates base^exponent."""
        try:
            return float(math.pow(base, exponent))
        except OverflowError:
            raise OverflowError("Result exceeds maximum numerical limit")

    @staticmethod
    def sqrt(x: Number) -> float:
        """Calculates square root √x."""
        if x < 0:
            raise ValueError("Square root domain error: cannot compute √ of negative number")
        return math.sqrt(x)

    @staticmethod
    def cbrt(x: Number) -> float:
        """Calculates cube root ∛x."""
        return math.cbrt(x) if hasattr(math, "cbrt") else (math.copysign(abs(x) ** (1 / 3), x))

    @staticmethod
    def factorial(n: Number) -> int:
        """Calculates n! (factorial) for non-negative integers."""
        if n < 0 or not float(n).is_integer():
            raise ValueError("Factorial is only defined for non-negative integers")
        if n > 170:
            raise OverflowError("Factorial input too large (n > 170 overflows float)")
        return math.factorial(int(n))

    @staticmethod
    def reciprocal(x: Number) -> float:
        """Calculates 1/x."""
        if x == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return 1.0 / x

    @staticmethod
    def percentage(x: Number) -> float:
        """Converts number to percentage value (x / 100)."""
        return x / 100.0

    @staticmethod
    def abs_val(x: Number) -> float:
        """Calculates absolute value |x|."""
        return abs(float(x))
