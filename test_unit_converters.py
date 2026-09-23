"""
test_unit_converters.py
=======================
Unit tests for UnitConverterEngine across all 12 physical and digital measurement categories.
"""

import math
import unittest
from unit_converter_engine import UnitConverterEngine


class TestUnitConverterEngine(unittest.TestCase):
    """Exhaustive test suite for UnitConverterEngine."""

    # -------------------------------------------------------------------------
    # 1. Volume
    # -------------------------------------------------------------------------
    def test_volume_conversions(self):
        # 1 Gallon (US) = 3.785411784 Liters
        ok, res, err = UnitConverterEngine.convert("volume", 1.0, "Gallons (US)", "Liters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 3.785411784, places=6)

        # 1 Liter = 1000 Milliliters
        ok, res, _ = UnitConverterEngine.convert("volume", 1.0, "Liters", "Milliliters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000.0, places=4)

        # 1 Milliliter = 1 Cubic centimeter
        ok, res, _ = UnitConverterEngine.convert("volume", 50.0, "Milliliters", "Cubic centimeters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 50.0, places=4)

        # 1 Cubic meter = 1000 Liters
        ok, res, _ = UnitConverterEngine.convert("volume", 2.5, "Cubic meters", "Liters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 2500.0, places=4)

        # Gallons to Quarts (1 gal = 4 qt)
        ok, res, _ = UnitConverterEngine.convert("volume", 2.0, "Gallons (US)", "Quarts (US)")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 8.0, places=4)

    # -------------------------------------------------------------------------
    # 2. Length
    # -------------------------------------------------------------------------
    def test_length_conversions(self):
        # 1 Meter = 1000 Millimeters
        ok, res, _ = UnitConverterEngine.convert("length", 1.0, "Meters", "Millimeters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000.0, places=4)

        # 1 Foot = 12 Inches = 0.3048 Meters
        ok, res, _ = UnitConverterEngine.convert("length", 1.0, "Feet", "Inches")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 12.0, places=4)

        # 1 Mile = 1.609344 Kilometers
        ok, res, _ = UnitConverterEngine.convert("length", 1.0, "Miles", "Kilometers")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1.609344, places=5)

        # 1 Nautical mile = 1852 Meters
        ok, res, _ = UnitConverterEngine.convert("length", 1.0, "Nautical miles", "Meters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1852.0, places=4)

    # -------------------------------------------------------------------------
    # 3. Weight and Mass
    # -------------------------------------------------------------------------
    def test_weight_conversions(self):
        # 1 Kilogram = 2.20462262 Pounds
        ok, res, _ = UnitConverterEngine.convert("weight", 1.0, "Kilograms", "Pounds")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 2.20462262, places=4)

        # 1 Pound = 16 Ounces
        ok, res, _ = UnitConverterEngine.convert("weight", 1.0, "Pounds", "Ounces")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 16.0, places=4)

        # 1 Stone = 14 Pounds
        ok, res, _ = UnitConverterEngine.convert("weight", 1.0, "Stones", "Pounds")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 14.0, places=4)

        # 1 Metric ton = 1000 Kilograms
        ok, res, _ = UnitConverterEngine.convert("weight", 3.0, "Metric tons", "Kilograms")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 3000.0, places=4)

    # -------------------------------------------------------------------------
    # 4. Temperature (Non-linear & Absolute Zero)
    # -------------------------------------------------------------------------
    def test_temperature_conversions(self):
        # 0 °C = 32 °F
        ok, res, _ = UnitConverterEngine.convert("temperature", 0.0, "Celsius", "Fahrenheit")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 32.0, places=4)

        # 100 °C = 212 °F
        ok, res, _ = UnitConverterEngine.convert("temperature", 100.0, "Celsius", "Fahrenheit")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 212.0, places=4)

        # -40 °C = -40 °F
        ok, res, _ = UnitConverterEngine.convert("temperature", -40.0, "Celsius", "Fahrenheit")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, -40.0, places=4)

        # 0 °C = 273.15 K
        ok, res, _ = UnitConverterEngine.convert("temperature", 0.0, "Celsius", "Kelvin")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 273.15, places=4)

        # Absolute zero: 0 K = -273.15 °C
        ok, res, _ = UnitConverterEngine.convert("temperature", 0.0, "Kelvin", "Celsius")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, -273.15, places=4)

        # Reject below absolute zero (Kelvin < 0)
        ok, res, err = UnitConverterEngine.convert("temperature", -5.0, "Kelvin", "Celsius")
        self.assertFalse(ok)
        self.assertIn("Kelvin cannot be negative", err)

        # Reject below absolute zero (Celsius < -273.15)
        ok, res, err = UnitConverterEngine.convert("temperature", -300.0, "Celsius", "Fahrenheit")
        self.assertFalse(ok)
        self.assertIn("below absolute zero", err)

        # Reject below absolute zero (Fahrenheit < -459.67)
        ok, res, err = UnitConverterEngine.convert("temperature", -500.0, "Fahrenheit", "Celsius")
        self.assertFalse(ok)
        self.assertIn("below absolute zero", err)

    # -------------------------------------------------------------------------
    # 5. Energy
    # -------------------------------------------------------------------------
    def test_energy_conversions(self):
        # 1 Kilojoule = 1000 Joules
        ok, res, _ = UnitConverterEngine.convert("energy", 1.0, "Kilojoules", "Joules")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000.0, places=4)

        # 1 Calorie = 4.184 Joules
        ok, res, _ = UnitConverterEngine.convert("energy", 1.0, "Calories", "Joules")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 4.184, places=4)

        # 1 Kilowatt-hour = 3.6e6 Joules
        ok, res, _ = UnitConverterEngine.convert("energy", 1.0, "Kilowatt-hours", "Joules")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 3600000.0, places=2)

    # -------------------------------------------------------------------------
    # 6. Area
    # -------------------------------------------------------------------------
    def test_area_conversions(self):
        # 1 Square meter = 10.76391 Square feet
        ok, res, _ = UnitConverterEngine.convert("area", 1.0, "Square meters", "Square feet")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 10.76391, places=4)

        # 1 Hectare = 10000 Square meters
        ok, res, _ = UnitConverterEngine.convert("area", 1.0, "Hectares", "Square meters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 10000.0, places=4)

        # 1 Acre = 4046.8564224 Square meters
        ok, res, _ = UnitConverterEngine.convert("area", 1.0, "Acres", "Square meters")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 4046.856, places=2)

    # -------------------------------------------------------------------------
    # 7. Speed
    # -------------------------------------------------------------------------
    def test_speed_conversions(self):
        # 100 km/h = 27.7778 m/s
        ok, res, _ = UnitConverterEngine.convert("speed", 100.0, "Kilometers per hour", "Meters per second")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 27.777778, places=4)

        # 60 mph = 96.56064 km/h
        ok, res, _ = UnitConverterEngine.convert("speed", 60.0, "Miles per hour", "Kilometers per hour")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 96.56064, places=4)

    # -------------------------------------------------------------------------
    # 8. Time
    # -------------------------------------------------------------------------
    def test_time_conversions(self):
        # 1 Hour = 60 Minutes = 3600 Seconds
        ok, res, _ = UnitConverterEngine.convert("time", 1.0, "Hours", "Minutes")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 60.0, places=4)

        ok, res, _ = UnitConverterEngine.convert("time", 1.0, "Hours", "Seconds")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 3600.0, places=4)

        # 1 Week = 7 Days
        ok, res, _ = UnitConverterEngine.convert("time", 2.0, "Weeks", "Days")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 14.0, places=4)

        # 1 Millisecond = 1000 Microseconds
        ok, res, _ = UnitConverterEngine.convert("time", 1.0, "Milliseconds", "Microseconds")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000.0, places=4)

    # -------------------------------------------------------------------------
    # 9. Power
    # -------------------------------------------------------------------------
    def test_power_conversions(self):
        # 1 Kilowatt = 1000 Watts
        ok, res, _ = UnitConverterEngine.convert("power", 1.0, "Kilowatts", "Watts")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000.0, places=4)

        # 1 Horsepower = 745.69987 Watts
        ok, res, _ = UnitConverterEngine.convert("power", 1.0, "Horsepower", "Watts")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 745.69987, places=4)

    # -------------------------------------------------------------------------
    # 10. Data (Decimal SI vs Binary IEC)
    # -------------------------------------------------------------------------
    def test_data_conversions(self):
        # 1 Byte = 8 Bits
        ok, res, _ = UnitConverterEngine.convert("data", 1.0, "Bytes", "Bits")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 8.0, places=4)

        # 1 Kilobyte (SI) = 1000 Bytes
        ok, res, _ = UnitConverterEngine.convert("data", 1.0, "Kilobytes", "Bytes")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000.0, places=4)

        # 1 Kibibyte (IEC) = 1024 Bytes
        ok, res, _ = UnitConverterEngine.convert("data", 1.0, "Kibibytes (KiB)", "Bytes")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1024.0, places=4)

        # 1 Megabyte (SI) = 1e6 Bytes
        ok, res, _ = UnitConverterEngine.convert("data", 1.0, "Megabytes", "Bytes")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1000000.0, places=4)

        # 1 Mebibyte (IEC) = 1048576 Bytes
        ok, res, _ = UnitConverterEngine.convert("data", 1.0, "Mebibytes (MiB)", "Bytes")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 1048576.0, places=4)

    # -------------------------------------------------------------------------
    # 11. Pressure
    # -------------------------------------------------------------------------
    def test_pressure_conversions(self):
        # 1 Atmosphere = 101325 Pascal = 14.69595 PSI
        ok, res, _ = UnitConverterEngine.convert("pressure", 1.0, "Atmosphere", "Pascal")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 101325.0, places=2)

        ok, res, _ = UnitConverterEngine.convert("pressure", 1.0, "Atmosphere", "PSI")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 14.69595, places=4)

        # 1 Bar = 100000 Pascal
        ok, res, _ = UnitConverterEngine.convert("pressure", 1.0, "Bar", "Pascal")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 100000.0, places=2)

    # -------------------------------------------------------------------------
    # 12. Angle
    # -------------------------------------------------------------------------
    def test_angle_conversions(self):
        # 180 Degrees = pi Radians
        ok, res, _ = UnitConverterEngine.convert("angle", 180.0, "Degrees", "Radians")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, math.pi, places=5)

        # 90 Degrees = 100 Gradians
        ok, res, _ = UnitConverterEngine.convert("angle", 90.0, "Degrees", "Gradians")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 100.0, places=4)

        # 1 Degree = 60 Arcminutes = 3600 Arcseconds
        ok, res, _ = UnitConverterEngine.convert("angle", 1.0, "Degrees", "Arcminutes")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 60.0, places=4)

        ok, res, _ = UnitConverterEngine.convert("angle", 1.0, "Degrees", "Arcseconds")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 3600.0, places=4)

    # -------------------------------------------------------------------------
    # Formatting & Formula
    # -------------------------------------------------------------------------
    def test_formatting_helper(self):
        self.assertEqual(UnitConverterEngine.format_value(0.0), "0")
        self.assertEqual(UnitConverterEngine.format_value(12.34000), "12.34")
        self.assertEqual(UnitConverterEngine.format_value(1000000.0), "1000000")
        # Extremely small
        self.assertIn("e-10", UnitConverterEngine.format_value(1e-10))
        # Formula string
        formula = UnitConverterEngine.get_rate_formula("length", "Meters", "Centimeters")
        self.assertEqual(formula, "1 Meters = 100 Centimeters")


if __name__ == "__main__":
    unittest.main()
