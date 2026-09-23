"""
unit_converter_engine.py
========================
Universal Unit Conversion Engine for 12 Physical and Digital Measurement Domains:
- Volume (Milliliters, Liters, Cubic centimeters, Cubic meters, Cubic inches, Cubic feet, Gallons, Quarts, Pints, Cups)
- Length (Millimeters, Centimeters, Meters, Kilometers, Inches, Feet, Yards, Miles, Nautical miles)
- Weight and Mass (Milligrams, Grams, Kilograms, Metric tons, Ounces, Pounds, Stones, US tons)
- Temperature (Celsius, Fahrenheit, Kelvin, with absolute zero physical validation)
- Energy (Joules, Kilojoules, Calories, Kilocalories, Watt-hours, Kilowatt-hours, Electronvolts, BTU)
- Area (Square millimeters, Square centimeters, Square meters, Square kilometers, Square inches, Square feet, Square yards, Acres, Hectares, Square miles)
- Speed (Meters per second, Kilometers per hour, Miles per hour, Feet per second, Knots)
- Time (Nanoseconds, Microseconds, Milliseconds, Seconds, Minutes, Hours, Days, Weeks)
- Power (Watts, Kilowatts, Megawatts, Horsepower, Metric horsepower, Foot-pounds per minute)
- Data (Bits, Bytes, Kilobits, Kilobytes, Megabits, Megabytes, Gigabits, Gigabytes, Terabits, Terabytes; plus Binary IEC: KiB, MiB, GiB, TiB)
- Pressure (Pascal, Kilopascal, Megapascal, Bar, Atmosphere, PSI, Torr, Millimeters of mercury)
- Angle (Degrees, Radians, Gradians, Arcminutes, Arcseconds)
"""

import math
from typing import Any, Dict, List, Optional, Tuple


class UnitConverterEngine:
    """
    Decoupled conversion engine operating on SI / canonical base units.
    Provides precise factors, non-linear temperature conversions,
    and adaptive decimal/scientific formatting.
    """

    # -------------------------------------------------------------------------
    # Conversion Registries (factor = value in base unit)
    # -------------------------------------------------------------------------
    REGISTRIES: Dict[str, Dict[str, Any]] = {
        # 1. Volume (Base Unit: Liter, L)
        "volume": {
            "base_unit": "Liters",
            "units": {
                "Milliliters": 0.001,
                "Liters": 1.0,
                "Cubic centimeters": 0.001,
                "Cubic meters": 1000.0,
                "Cubic inches": 0.016387064,
                "Cubic feet": 28.316846592,
                "Gallons (US)": 3.785411784,
                "Quarts (US)": 0.946352946,
                "Pints (US)": 0.473176473,
                "Cups (US)": 0.2365882365,
            },
            "default_from": "Liters",
            "default_to": "Gallons (US)",
        },

        # 2. Length (Base Unit: Meter, m)
        "length": {
            "base_unit": "Meters",
            "units": {
                "Millimeters": 0.001,
                "Centimeters": 0.01,
                "Meters": 1.0,
                "Kilometers": 1000.0,
                "Inches": 0.0254,
                "Feet": 0.3048,
                "Yards": 0.9144,
                "Miles": 1609.344,
                "Nautical miles": 1852.0,
            },
            "default_from": "Meters",
            "default_to": "Feet",
        },

        # 3. Weight and Mass (Base Unit: Kilogram, kg)
        "weight": {
            "base_unit": "Kilograms",
            "units": {
                "Milligrams": 1e-6,
                "Grams": 0.001,
                "Kilograms": 1.0,
                "Metric tons": 1000.0,
                "Ounces": 0.028349523125,
                "Pounds": 0.45359237,
                "Stones": 6.35029318,
                "US tons": 907.18474,
            },
            "default_from": "Kilograms",
            "default_to": "Pounds",
        },

        # 4. Temperature (Non-linear, handled by custom methods)
        "temperature": {
            "base_unit": "Celsius",
            "units": {
                "Celsius": 1.0,
                "Fahrenheit": 1.0,
                "Kelvin": 1.0,
            },
            "default_from": "Celsius",
            "default_to": "Fahrenheit",
        },

        # 5. Energy (Base Unit: Joule, J)
        "energy": {
            "base_unit": "Joules",
            "units": {
                "Joules": 1.0,
                "Kilojoules": 1000.0,
                "Calories": 4.184,
                "Kilocalories": 4184.0,
                "Watt-hours": 3600.0,
                "Kilowatt-hours": 3600000.0,
                "Electronvolts": 1.602176634e-19,
                "BTU": 1055.05585,
            },
            "default_from": "Kilowatt-hours",
            "default_to": "Joules",
        },

        # 6. Area (Base Unit: Square meter, m²)
        "area": {
            "base_unit": "Square meters",
            "units": {
                "Square millimeters": 1e-6,
                "Square centimeters": 0.0001,
                "Square meters": 1.0,
                "Square kilometers": 1e6,
                "Square inches": 0.00064516,
                "Square feet": 0.09290304,
                "Square yards": 0.83612736,
                "Acres": 4046.8564224,
                "Hectares": 10000.0,
                "Square miles": 2589988.110336,
            },
            "default_from": "Square meters",
            "default_to": "Square feet",
        },

        # 7. Speed (Base Unit: Meter per second, m/s)
        "speed": {
            "base_unit": "Meters per second",
            "units": {
                "Meters per second": 1.0,
                "Kilometers per hour": 1.0 / 3.6,
                "Miles per hour": 0.44704,
                "Feet per second": 0.3048,
                "Knots": 1852.0 / 3600.0,
            },
            "default_from": "Kilometers per hour",
            "default_to": "Miles per hour",
        },

        # 8. Time (Base Unit: Second, s)
        "time": {
            "base_unit": "Seconds",
            "units": {
                "Nanoseconds": 1e-9,
                "Microseconds": 1e-6,
                "Milliseconds": 0.001,
                "Seconds": 1.0,
                "Minutes": 60.0,
                "Hours": 3600.0,
                "Days": 86400.0,
                "Weeks": 604800.0,
            },
            "default_from": "Hours",
            "default_to": "Minutes",
        },

        # 9. Power (Base Unit: Watt, W)
        "power": {
            "base_unit": "Watts",
            "units": {
                "Watts": 1.0,
                "Kilowatts": 1000.0,
                "Megawatts": 1e6,
                "Horsepower": 745.69987158227,
                "Metric horsepower": 735.49875,
                "Foot-pounds per minute": 745.69987158227 / 33000.0,
            },
            "default_from": "Kilowatts",
            "default_to": "Horsepower",
        },

        # 10. Data (Base Unit: Byte, B)
        "data": {
            "base_unit": "Bytes",
            "units": {
                # Decimal (SI, powers of 1000)
                "Bits": 0.125,
                "Bytes": 1.0,
                "Kilobits": 125.0,
                "Kilobytes": 1000.0,
                "Megabits": 125000.0,
                "Megabytes": 1e6,
                "Gigabits": 1.25e8,
                "Gigabytes": 1e9,
                "Terabits": 1.25e11,
                "Terabytes": 1e12,
                # Binary (IEC, powers of 1024)
                "Kibibytes (KiB)": 1024.0,
                "Mebibytes (MiB)": 1024.0 ** 2,
                "Gibibytes (GiB)": 1024.0 ** 3,
                "Tebibytes (TiB)": 1024.0 ** 4,
            },
            "default_from": "Megabytes",
            "default_to": "Gigabytes",
        },

        # 11. Pressure (Base Unit: Pascal, Pa)
        "pressure": {
            "base_unit": "Pascal",
            "units": {
                "Pascal": 1.0,
                "Kilopascal": 1000.0,
                "Megapascal": 1e6,
                "Bar": 100000.0,
                "Atmosphere": 101325.0,
                "PSI": 6894.757293168,
                "Torr": 101325.0 / 760.0,
                "Millimeters of mercury": 133.322387415,
            },
            "default_from": "Atmosphere",
            "default_to": "PSI",
        },

        # 12. Angle (Base Unit: Radians, rad)
        "angle": {
            "base_unit": "Radians",
            "units": {
                "Degrees": math.pi / 180.0,
                "Radians": 1.0,
                "Gradians": math.pi / 200.0,
                "Arcminutes": math.pi / (180.0 * 60.0),
                "Arcseconds": math.pi / (180.0 * 3600.0),
            },
            "default_from": "Degrees",
            "default_to": "Radians",
        },
    }

    # -------------------------------------------------------------------------
    # Core Conversion Method
    # -------------------------------------------------------------------------
    @classmethod
    def convert(
        cls,
        category: str,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Converts a numeric value from from_unit to to_unit within the specified category.
        Returns (success: bool, result_value: Optional[float], error_message: Optional[str]).
        """
        cat_key = category.lower().strip()
        if cat_key not in cls.REGISTRIES:
            return False, None, f"Unknown conversion category: '{category}'"

        cat_info = cls.REGISTRIES[cat_key]
        units_map = cat_info["units"]

        if from_unit not in units_map:
            return False, None, f"Unknown unit: '{from_unit}' in category '{category}'"
        if to_unit not in units_map:
            return False, None, f"Unknown unit: '{to_unit}' in category '{category}'"

        # Identity conversion
        if from_unit == to_unit:
            return True, float(value), None

        # Special Non-linear case: Temperature
        if cat_key == "temperature":
            return cls._convert_temperature(value, from_unit, to_unit)

        # Standard linear base-unit conversion
        from_factor = units_map[from_unit]
        to_factor = units_map[to_unit]

        base_value = value * from_factor
        result_value = base_value / to_factor
        return True, result_value, None

    # -------------------------------------------------------------------------
    # Temperature Conversions & Absolute Zero Handling
    # -------------------------------------------------------------------------
    @classmethod
    def _convert_temperature(
        cls,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Converts temperature between Celsius, Fahrenheit, and Kelvin.
        Validates that temperature is not below absolute zero (0 K).
        """
        # Step 1: Convert from_unit to Kelvin
        if from_unit == "Celsius":
            kelvin = value + 273.15
        elif from_unit == "Fahrenheit":
            kelvin = (value - 32.0) * (5.0 / 9.0) + 273.15
        elif from_unit == "Kelvin":
            kelvin = value
        else:
            return False, None, f"Unsupported temperature unit: {from_unit}"

        # Physical validation: Cannot be below absolute zero
        if kelvin < -1e-9:  # Small epsilon for float rounding around 0
            if from_unit == "Kelvin":
                return False, None, "Kelvin cannot be negative (Absolute zero is 0 K)"
            elif from_unit == "Celsius":
                return False, None, "Temperature cannot be below absolute zero (-273.15 °C)"
            else:
                return False, None, "Temperature cannot be below absolute zero (-459.67 °F)"

        # Step 2: Convert Kelvin to to_unit
        if to_unit == "Celsius":
            result = kelvin - 273.15
        elif to_unit == "Fahrenheit":
            result = (kelvin - 273.15) * (9.0 / 5.0) + 32.0
        elif to_unit == "Kelvin":
            result = kelvin
        else:
            return False, None, f"Unsupported temperature unit: {to_unit}"

        return True, result, None

    # -------------------------------------------------------------------------
    # Unit Metadata Helpers
    # -------------------------------------------------------------------------
    @classmethod
    def get_unit_list(cls, category: str, system: Optional[str] = None) -> List[str]:
        """
        Returns the ordered list of units for a category.
        For 'data', system can be 'all', 'si', or 'iec'.
        """
        cat_key = category.lower().strip()
        if cat_key not in cls.REGISTRIES:
            return []

        all_units = list(cls.REGISTRIES[cat_key]["units"].keys())
        if cat_key == "data" and system in ("si", "iec"):
            if system == "iec":
                return [u for u in all_units if "KiB" in u or "MiB" in u or "GiB" in u or "TiB" in u or u == "Bytes"]
            else:
                return [u for u in all_units if not ("KiB" in u or "MiB" in u or "GiB" in u or "TiB" in u)]
        return all_units

    @classmethod
    def get_defaults(cls, category: str) -> Tuple[str, str]:
        """Returns (default_from_unit, default_to_unit)."""
        cat_key = category.lower().strip()
        if cat_key in cls.REGISTRIES:
            info = cls.REGISTRIES[cat_key]
            return info.get("default_from", ""), info.get("default_to", "")
        return "", ""

    # -------------------------------------------------------------------------
    # Formatting Helpers
    # -------------------------------------------------------------------------
    @classmethod
    def format_value(cls, val: float, max_sig_digits: int = 8) -> str:
        """
        Formats float into a human-readable clean string without trailing float noise.
        Uses clean scientific notation for numbers with magnitude < 1e-6 or >= 1e12.
        """
        if math.isnan(val):
            return "NaN"
        if math.isinf(val):
            return "Infinity" if val > 0 else "-Infinity"

        abs_val = abs(val)
        if abs_val == 0.0:
            return "0"

        # Scientific notation for very small or very large values
        if abs_val < 1e-6 or abs_val >= 1e12:
            formatted = f"{val:.6e}"
            # Clean up mantissa trailing zeros
            mantissa, exp = formatted.split("e")
            mantissa = mantissa.rstrip("0").rstrip(".")
            exp_int = int(exp)
            return f"{mantissa}e{exp_int:+d}"

        # Standard decimal formatting rounded to max_sig_digits significant digits
        formatted = f"{val:.{max_sig_digits}g}"
        # Check if python chose exponential form
        if "e" in formatted:
            mantissa, exp = formatted.split("e")
            return f"{mantissa}e{int(exp):+d}"

        # Strip unnecessary trailing decimal zeros
        if "." in formatted:
            formatted = formatted.rstrip("0").rstrip(".")
        return formatted

    @classmethod
    def get_rate_formula(cls, category: str, from_unit: str, to_unit: str) -> str:
        """Returns a string describing the relationship, e.g. '1 m = 3.28084 ft'."""
        success, factor, _ = cls.convert(category, 1.0, from_unit, to_unit)
        if not success or factor is None:
            return ""
        formatted_factor = cls.format_value(factor)
        return f"1 {from_unit} = {formatted_factor} {to_unit}"
