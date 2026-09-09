"""
test_calculator.py
==================
Unit tests for ScientificEngine, CalculatorEngine, and HistoryManager.
"""

import unittest
import os
import math
from scientific import ScientificEngine
from calculator import CalculatorEngine, SafeMathEvaluator
from history import HistoryManager


class TestScientificEngine(unittest.TestCase):

    def test_trigonometry_deg(self):
        self.assertAlmostEqual(ScientificEngine.sin(30, mode="DEG"), 0.5, places=5)
        self.assertAlmostEqual(ScientificEngine.sin(90, mode="DEG"), 1.0, places=5)
        self.assertAlmostEqual(ScientificEngine.sin(180, mode="DEG"), 0.0, places=5)
        self.assertAlmostEqual(ScientificEngine.cos(60, mode="DEG"), 0.5, places=5)
        self.assertAlmostEqual(ScientificEngine.cos(0, mode="DEG"), 1.0, places=5)
        self.assertAlmostEqual(ScientificEngine.tan(45, mode="DEG"), 1.0, places=5)

    def test_trigonometry_rad(self):
        self.assertAlmostEqual(ScientificEngine.sin(math.pi / 2, mode="RAD"), 1.0, places=5)
        self.assertAlmostEqual(ScientificEngine.cos(math.pi, mode="RAD"), -1.0, places=5)

    def test_inverse_trigonometry(self):
        self.assertAlmostEqual(ScientificEngine.asin(0.5, mode="DEG"), 30.0, places=5)
        self.assertAlmostEqual(ScientificEngine.acos(0.5, mode="DEG"), 60.0, places=5)
        self.assertAlmostEqual(ScientificEngine.atan(1.0, mode="DEG"), 45.0, places=5)

    def test_logarithms(self):
        self.assertAlmostEqual(ScientificEngine.log10(100), 2.0, places=5)
        self.assertAlmostEqual(ScientificEngine.ln(math.e), 1.0, places=5)
        self.assertAlmostEqual(ScientificEngine.log2(8), 3.0, places=5)
        with self.assertRaises(ValueError):
            ScientificEngine.log10(-5)

    def test_powers_and_roots(self):
        self.assertEqual(ScientificEngine.square(5), 25.0)
        self.assertEqual(ScientificEngine.cube(3), 27.0)
        self.assertEqual(ScientificEngine.power(2, 4), 16.0)
        self.assertEqual(ScientificEngine.sqrt(49), 7.0)
        with self.assertRaises(ValueError):
            ScientificEngine.sqrt(-4)

    def test_factorial(self):
        self.assertEqual(ScientificEngine.factorial(0), 1)
        self.assertEqual(ScientificEngine.factorial(5), 120)
        self.assertEqual(ScientificEngine.factorial(6), 720)
        with self.assertRaises(ValueError):
            ScientificEngine.factorial(-1)

    def test_reciprocal_and_percentage(self):
        self.assertEqual(ScientificEngine.reciprocal(4), 0.25)
        self.assertEqual(ScientificEngine.percentage(50), 0.5)
        with self.assertRaises(ZeroDivisionError):
            ScientificEngine.reciprocal(0)


class TestSafeMathEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator_deg = SafeMathEvaluator(angle_mode="DEG")
        self.evaluator_rad = SafeMathEvaluator(angle_mode="RAD")

    def test_basic_arithmetic(self):
        self.assertEqual(self.evaluator_deg.evaluate("2 + 3"), 5)
        self.assertEqual(self.evaluator_deg.evaluate("10 - 4"), 6)
        self.assertEqual(self.evaluator_deg.evaluate("6 * 7"), 42)
        self.assertEqual(self.evaluator_deg.evaluate("15 / 3"), 5)

    def test_operator_precedence(self):
        self.assertEqual(self.evaluator_deg.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.evaluator_deg.evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(self.evaluator_deg.evaluate("2 ** 3 + 1"), 9)

    def test_scientific_functions(self):
        self.assertAlmostEqual(self.evaluator_deg.evaluate("sin(30)"), 0.5, places=5)
        self.assertAlmostEqual(self.evaluator_deg.evaluate("cos(60) + sin(30)"), 1.0, places=5)
        self.assertEqual(self.evaluator_deg.evaluate("sqrt(25) + 3"), 8)
        self.assertEqual(self.evaluator_deg.evaluate("fact(4)"), 24)

    def test_security_disallowed_syntax(self):
        # Disallow arbitrary code execution attempts
        with self.assertRaises(Exception):
            self.evaluator_deg.evaluate("__import__('os').system('dir')")
        with self.assertRaises(Exception):
            self.evaluator_deg.evaluate("open('test.txt', 'w')")


class TestCalculatorEngine(unittest.TestCase):

    def setUp(self):
        test_history_file = os.path.join(os.path.dirname(__file__), "test_history.json")
        self.history = HistoryManager(storage_file=test_history_file)
        self.history.clear()
        self.calc = CalculatorEngine(history_manager=self.history)

    def tearDown(self):
        self.history.clear()
        if os.path.exists(self.history.storage_file):
            os.remove(self.history.storage_file)

    def test_number_and_operator_input(self):
        self.calc.append_number("1")
        self.calc.append_number("2")
        self.assertEqual(self.calc.current_input, "12")
        self.calc.append_operator("+")
        self.calc.append_number("8")
        self.assertEqual(self.calc.calculate(), "20")
        self.assertEqual(self.calc.previous_expression, "12 + 8 =")

    def test_basic_subtraction_and_multiplication(self):
        self.calc.current_input = "5 × 4 + 2"
        self.assertEqual(self.calc.calculate(), "22")

        self.calc.current_input = "50 − 20"
        self.assertEqual(self.calc.calculate(), "30")

    def test_decimals(self):
        self.calc.append_number("3")
        self.calc.append_decimal()
        self.calc.append_number("14")
        self.calc.append_decimal()  # Should be ignored (no duplicate dot)
        self.assertEqual(self.calc.current_input, "3.14")
        self.calc.append_operator("+")
        self.calc.append_decimal()  # Should become ' 0.'
        self.calc.append_number("86")
        self.assertEqual(self.calc.calculate(), "4")

    def test_negative_numbers_and_sign_toggle(self):
        self.calc.current_input = "5"
        self.calc.toggle_sign()
        self.assertEqual(self.calc.current_input, "-5")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.current_input, "5")

        # Negative in expression
        self.calc.current_input = "-5 + 3"
        self.assertEqual(self.calc.calculate(), "-2")

        # Multiplying negative
        self.calc.current_input = "5 × -2"
        self.assertEqual(self.calc.calculate(), "-10")

    def test_percentages(self):
        self.calc.current_input = "50%"
        self.assertEqual(self.calc.calculate(), "0.5")

        self.calc.current_input = "200 × 15%"
        self.assertEqual(self.calc.calculate(), "30")

    def test_parentheses_and_precedence(self):
        # Explicit parentheses
        self.calc.current_input = "(2 + 3) × 4"
        self.assertEqual(self.calc.calculate(), "20")

        # Implicit multiplication 5(2+3)
        self.calc.current_input = "5(2 + 3)"
        self.assertEqual(self.calc.calculate(), "25")

        # Auto-closing parentheses
        self.calc.current_input = "(10 + 5"
        self.assertEqual(self.calc.calculate(), "15")

    def test_division_by_zero(self):
        self.calc.current_input = "10 ÷ 0"
        res = self.calc.calculate()
        self.assertIn("Division by zero", res)

        self.calc.current_input = "5 / (2 - 2)"
        res = self.calc.calculate()
        self.assertIn("Division by zero", res)

    def test_invalid_expressions_handled_gracefully(self):
        self.calc.current_input = "5 / * 2"
        res = self.calc.calculate()
        self.assertIn("Error", res)

        self.calc.current_input = "()"
        res = self.calc.calculate()
        self.assertIn("Error", res)

    def test_backspace(self):
        self.calc.current_input = "1234"
        self.calc.backspace()
        self.assertEqual(self.calc.current_input, "123")

    def test_clear_and_all_clear(self):
        self.calc.current_input = "123"
        self.calc.previous_expression = "10 + 2 ="
        self.calc.clear()
        self.assertEqual(self.calc.current_input, "0")
        self.assertEqual(self.calc.previous_expression, "10 + 2 =")

        self.calc.all_clear()
        self.assertEqual(self.calc.current_input, "0")
        self.assertEqual(self.calc.previous_expression, "")

    def test_memory_operations(self):
        self.calc.current_input = "50"
        self.calc.memory_store()
        self.assertTrue(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 50.0)

        self.calc.current_input = "25"
        self.calc.memory_add()
        self.assertEqual(self.calc.memory_value, 75.0)

        self.calc.current_input = "10"
        self.calc.memory_subtract()
        self.assertEqual(self.calc.memory_value, 65.0)

        self.calc.current_input = "0"
        self.calc.memory_recall()
        self.assertEqual(self.calc.current_input, "65")

        self.calc.memory_clear()
        self.assertFalse(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 0.0)

    def test_history_integration(self):
        self.calc.current_input = "7 × 8"
        self.calc.calculate()
        entries = self.history.get_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].expression, "7 × 8")
        self.assertEqual(entries[0].result, "56")


if __name__ == "__main__":
    unittest.main()
