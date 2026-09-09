"""
scientific.py
=============
Scientific calculation module powered strictly by Python's built-in `math` library.

This module provides pure mathematical functions isolated from any user interface.
It validates all inputs, handles edge cases (e.g. negative square roots, invalid factorials,
division by zero, overflow limits, domain limits), and eliminates floating-point epsilon noise.
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
            return math.radians(float(angle))
        return float(angle)

    @staticmethod
    def _from_radians(angle_rad: float, mode: str = "DEG") -> float:
        """Converts radians to degrees if mode is DEG, otherwise leaves as RAD."""
        if mode.upper() == "DEG":
            return math.degrees(angle_rad)
        return angle_rad

    # -------------------------------------------------------------------------
    # Trigonometric Functions (sin, cos, tan)
    # -------------------------------------------------------------------------
    @classmethod
    def sin(cls, x: Number, mode: str = "DEG") -> float:
        """
        Calculates sine of x in DEG or RAD mode.
        sin(30) in DEG returns 0.5; sin(pi/6) in RAD returns 0.5.
        """
        rad = cls._to_radians(x, mode)
        val = round(math.sin(rad), 12)
        return 0.0 if abs(val) < 1e-12 else val

    @classmethod
    def cos(cls, x: Number, mode: str = "DEG") -> float:
        """
        Calculates cosine of x in DEG or RAD mode.
        cos(60) in DEG returns 0.5; cos(0) returns 1.0.
        """
        rad = cls._to_radians(x, mode)
        val = round(math.cos(rad), 12)
        return 0.0 if abs(val) < 1e-12 else val

    @classmethod
    def tan(cls, x: Number, mode: str = "DEG") -> float:
        """
        Calculates tangent of x in DEG or RAD mode.
        Safely detects undefined values (e.g. at 90°, 270°) and raises ZeroDivisionError.
        """
        rad = cls._to_radians(x, mode)
        c = round(math.cos(rad), 12)
        if abs(c) < 1e-12:
            raise ZeroDivisionError("Tangent undefined (division by zero at 90° + k*180°)")
        val = round(math.tan(rad), 12)
        return 0.0 if abs(val) < 1e-12 else val

    # -------------------------------------------------------------------------
    # Inverse Trigonometric Functions (asin, acos, atan)
    # -------------------------------------------------------------------------
    @classmethod
    def asin(cls, x: Number, mode: str = "DEG") -> float:
        """
        Calculates arcsine (inverse sine) in DEG or RAD.
        Domain: [-1, 1]. Returns error if outside domain.
        """
        val = float(x)
        if not -1.0 <= val <= 1.0:
            raise ValueError("Arcsin requires input between -1 and 1")
        res = cls._from_radians(math.asin(val), mode)
        rounded = round(res, 12)
        return 0.0 if abs(rounded) < 1e-12 else rounded

    @classmethod
    def acos(cls, x: Number, mode: str = "DEG") -> float:
        """
        Calculates arccosine (inverse cosine) in DEG or RAD.
        Domain: [-1, 1]. Returns error if outside domain.
        """
        val = float(x)
        if not -1.0 <= val <= 1.0:
            raise ValueError("Arccos requires input between -1 and 1")
        res = cls._from_radians(math.acos(val), mode)
        rounded = round(res, 12)
        return 0.0 if abs(rounded) < 1e-12 else rounded

    @classmethod
    def atan(cls, x: Number, mode: str = "DEG") -> float:
        """
        Calculates arctangent (inverse tangent) in DEG or RAD.
        Domain: all real numbers.
        """
        res = cls._from_radians(math.atan(float(x)), mode)
        rounded = round(res, 12)
        return 0.0 if abs(rounded) < 1e-12 else rounded

    # -------------------------------------------------------------------------
    # Hyperbolic Functions
    # -------------------------------------------------------------------------
    @staticmethod
    def sinh(x: Number) -> float:
        """Hyperbolic sine with overflow protection."""
        try:
            return math.sinh(float(x))
        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def cosh(x: Number) -> float:
        """Hyperbolic cosine with overflow protection."""
        try:
            return math.cosh(float(x))
        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def tanh(x: Number) -> float:
        """Hyperbolic tangent."""
        return math.tanh(float(x))

    # -------------------------------------------------------------------------
    # Logarithmic & Exponential Functions
    # -------------------------------------------------------------------------
    @staticmethod
    def ln(x: Number) -> float:
        """
        Natural logarithm (base e).
        Validates domain x > 0.
        """
        val = float(x)
        if val <= 0:
            raise ValueError("Natural log requires value > 0")
        return math.log(val)

    @staticmethod
    def log10(x: Number) -> float:
        """
        Common logarithm (base 10).
        Validates domain x > 0.
        """
        val = float(x)
        if val <= 0:
            raise ValueError("Logarithm requires value > 0")
        return math.log10(val)

    @staticmethod
    def log2(x: Number) -> float:
        """Logarithm base 2 with domain validation."""
        val = float(x)
        if val <= 0:
            raise ValueError("Logarithm requires value > 0")
        return math.log2(val)

    @staticmethod
    def exp(x: Number) -> float:
        """
        Exponential function e^x with overflow protection.
        """
        try:
            return math.exp(float(x))
        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def pow10(x: Number) -> float:
        """Calculates 10^x with overflow protection."""
        try:
            return math.pow(10, float(x))
        except OverflowError:
            raise OverflowError("Result too large")

    # -------------------------------------------------------------------------
    # Advanced Mathematical Operations
    # -------------------------------------------------------------------------
    @staticmethod
    def square(x: Number) -> float:
        """Calculates x² with overflow prevention."""
        try:
            val = float(x)
            res = val ** 2
            if math.isinf(res):
                raise OverflowError("Result too large")
            return res
        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def cube(x: Number) -> float:
        """Calculates x³ with overflow protection."""
        try:
            val = float(x)
            res = val ** 3
            if math.isinf(res):
                raise OverflowError("Result too large")
            return res
        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def sqrt(x: Number) -> float:
        """
        Calculates square root √x.
        Safely validates and rejects negative numbers with friendly error.
        """
        val = float(x)
        if val < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(val)

    @staticmethod
    def cbrt(x: Number) -> float:
        """Calculates cube root ∛x."""
        val = float(x)
        return math.cbrt(val) if hasattr(math, "cbrt") else (math.copysign(abs(val) ** (1 / 3), val))

    @staticmethod
    def power(base: Number, exponent: Number) -> float:
        """
        Calculates base^exponent (xʸ).
        Validates negative base with fractional exponents, division by zero, and overflow.
        """
        try:
            b = float(base)
            exp = float(exponent)

            # Check division by zero: e.g. 0^-2
            if b == 0 and exp < 0:
                raise ZeroDivisionError("Cannot divide by zero")

            # Check complex/imaginary results: negative base with fractional exponent
            if b < 0 and not exp.is_integer():
                raise ValueError("Negative base cannot have fractional exponent")

            res = math.pow(b, exp)
            if math.isinf(res):
                raise OverflowError("Result too large")
            return float(res)

        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def factorial(n: Number) -> int:
        """
        Calculates n! (factorial).
        Properly validates:
        - Must be non-negative (n >= 0)
        - Must be an integer (no decimals like 4.5!)
        - Prevents overflow: float limit is 170! (171! overflows)
        """
        try:
            val = float(n)
        except (ValueError, TypeError):
            raise ValueError("Factorial requires a valid number")

        if val < 0:
            raise ValueError("Factorial requires a non-negative number")
        if not val.is_integer():
            raise ValueError("Factorial is only defined for integers")
        if val > 170:
            raise OverflowError("Factorial input too large (maximum 170)")

        return math.factorial(int(val))

    @staticmethod
    def reciprocal(x: Number) -> float:
        """
        Calculates 1/x (reciprocal).
        Validates non-zero input to prevent division by zero.
        """
        val = float(x)
        if val == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        try:
            res = 1.0 / val
            if math.isinf(res):
                raise OverflowError("Result too large")
            return res
        except OverflowError:
            raise OverflowError("Result too large")

    @staticmethod
    def percentage(x: Number) -> float:
        """Converts number to percentage value (x / 100)."""
        return float(x) / 100.0

    @staticmethod
    def abs_val(x: Number) -> float:
        """Calculates absolute value |x|."""
        return abs(float(x))
