"""
test_calculator.py
==================
Unit tests for ScientificEngine, CalculatorEngine, and HistoryManager.
Comprehensive coverage of basic arithmetic and advanced mathematical operations:
- Square (x²)
- Square root (√x)
- Power (xʸ)
- Percentage (%)
- Reciprocal (1/x)
- Plus/minus (±)
- Factorial (x!)
- Absolute value (|x|)
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

    def test_hyperbolic_functions(self):
        self.assertAlmostEqual(ScientificEngine.sinh(0), 0.0, places=5)
        self.assertAlmostEqual(ScientificEngine.cosh(0), 1.0, places=5)
        self.assertAlmostEqual(ScientificEngine.tanh(0), 0.0, places=5)
        self.assertAlmostEqual(ScientificEngine.sinh(1), math.sinh(1), places=5)

    def test_custom_base_logarithm(self):
        self.assertAlmostEqual(ScientificEngine.log_base(8, 2), 3.0, places=5)
        self.assertAlmostEqual(ScientificEngine.log_base(1000, 10), 3.0, places=5)
        self.assertAlmostEqual(ScientificEngine.log_base(81, 3), 4.0, places=5)
        with self.assertRaises(ValueError):
            ScientificEngine.log_base(-8, 2)
        with self.assertRaises(ValueError):
            ScientificEngine.log_base(8, -2)
        with self.assertRaises(ValueError):
            ScientificEngine.log_base(8, 1)

    def test_cube_root(self):
        self.assertAlmostEqual(ScientificEngine.cbrt(27), 3.0, places=5)
        self.assertAlmostEqual(ScientificEngine.cbrt(-8), -2.0, places=5)
        self.assertEqual(ScientificEngine.cbrt(0), 0.0)

    # -------------------------------------------------------------------------
    # Advanced Mathematical Operations Tests
    # -------------------------------------------------------------------------
    def test_square_and_overflow(self):
        self.assertEqual(ScientificEngine.square(5), 25.0)
        self.assertEqual(ScientificEngine.square(-4), 16.0)
        self.assertEqual(ScientificEngine.square(0), 0.0)
        with self.assertRaises(OverflowError):
            ScientificEngine.square(1e200)

    def test_square_root_positive_and_negative(self):
        self.assertEqual(ScientificEngine.sqrt(49), 7.0)
        self.assertEqual(ScientificEngine.sqrt(0), 0.0)
        with self.assertRaises(ValueError) as ctx:
            ScientificEngine.sqrt(-16)
        self.assertIn("negative number", str(ctx.exception).lower())

    def test_power_and_edge_cases(self):
        self.assertEqual(ScientificEngine.power(2, 4), 16.0)
        self.assertEqual(ScientificEngine.power(5, 0), 1.0)
        self.assertEqual(ScientificEngine.power(-2, 3), -8.0)
        # Negative base with fractional exponent
        with self.assertRaises(ValueError):
            ScientificEngine.power(-4, 0.5)
        # 0 to negative exponent
        with self.assertRaises(ZeroDivisionError):
            ScientificEngine.power(0, -2)
        # Overflow
        with self.assertRaises(OverflowError):
            ScientificEngine.power(10, 500)

    def test_percentage(self):
        self.assertEqual(ScientificEngine.percentage(50), 0.5)
        self.assertEqual(ScientificEngine.percentage(100), 1.0)
        self.assertEqual(ScientificEngine.percentage(0), 0.0)

    def test_reciprocal(self):
        self.assertEqual(ScientificEngine.reciprocal(4), 0.25)
        self.assertEqual(ScientificEngine.reciprocal(-2), -0.5)
        with self.assertRaises(ZeroDivisionError):
            ScientificEngine.reciprocal(0)

    def test_factorial_valid_and_invalid(self):
        self.assertEqual(ScientificEngine.factorial(0), 1)
        self.assertEqual(ScientificEngine.factorial(1), 1)
        self.assertEqual(ScientificEngine.factorial(5), 120)
        self.assertEqual(ScientificEngine.factorial(6), 720)
        # Negative number
        with self.assertRaises(ValueError) as ctx:
            ScientificEngine.factorial(-3)
        self.assertIn("non-negative", str(ctx.exception).lower())
        # Decimals
        with self.assertRaises(ValueError) as ctx:
            ScientificEngine.factorial(4.5)
        self.assertIn("integer", str(ctx.exception).lower())
        # Overflow beyond 170!
        with self.assertRaises(OverflowError):
            ScientificEngine.factorial(171)

    def test_absolute_value(self):
        self.assertEqual(ScientificEngine.abs_val(-5), 5.0)
        self.assertEqual(ScientificEngine.abs_val(5), 5.0)
        self.assertEqual(ScientificEngine.abs_val(-3.14), 3.14)
        self.assertEqual(ScientificEngine.abs_val(0), 0.0)


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
        self.assertEqual(self.evaluator_deg.evaluate("abs(-15)"), 15)
        self.assertEqual(self.evaluator_deg.evaluate("sqr(6)"), 36)
        self.assertEqual(self.evaluator_deg.evaluate("recip(4)"), 0.25)

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

    def test_advanced_square_and_power(self):
        self.calc.current_input = "6"
        self.assertEqual(self.calc.apply_unary_operation("sqr"), "36")

        self.calc.current_input = "3 ^ 3"
        self.assertEqual(self.calc.calculate(), "27")

    def test_advanced_sqrt_and_negative_handling(self):
        self.calc.current_input = "64"
        self.assertEqual(self.calc.apply_unary_operation("sqrt"), "8")

        # Negative square root friendly error
        self.calc.current_input = "-16"
        res = self.calc.apply_unary_operation("sqrt")
        self.assertEqual(res, "Math domain error")

    def test_advanced_reciprocal(self):
        self.calc.current_input = "4"
        self.assertEqual(self.calc.apply_unary_operation("recip"), "0.25")

        self.calc.current_input = "0"
        res = self.calc.apply_unary_operation("recip")
        self.assertEqual(res, "Cannot divide by zero")

    def test_advanced_absolute_value(self):
        self.calc.current_input = "-42"
        self.assertEqual(self.calc.apply_unary_operation("abs"), "42")

        self.calc.current_input = "|-18| + 2"
        self.assertEqual(self.calc.calculate(), "20")

    def test_advanced_factorial_valid_and_invalid(self):
        self.calc.current_input = "5"
        self.assertEqual(self.calc.apply_unary_operation("fact"), "120")

        self.calc.current_input = "-4"
        res = self.calc.apply_unary_operation("fact")
        self.assertEqual(res, "Math domain error")

        self.calc.current_input = "3.2"
        res = self.calc.apply_unary_operation("fact")
        self.assertEqual(res, "Math domain error")

    def test_negative_numbers_and_sign_toggle(self):
        self.calc.current_input = "5"
        self.calc.toggle_sign()
        self.assertEqual(self.calc.current_input, "-5")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.current_input, "5")

        self.calc.current_input = "-5 + 3"
        self.assertEqual(self.calc.calculate(), "-2")

        self.calc.current_input = "5 × -2"
        self.assertEqual(self.calc.calculate(), "-10")

    def test_percentages(self):
        self.calc.current_input = "50%"
        self.assertEqual(self.calc.calculate(), "0.5")

        self.calc.current_input = "200 × 15%"
        self.assertEqual(self.calc.calculate(), "30")

    def test_parentheses_and_precedence(self):
        self.calc.current_input = "(2 + 3) × 4"
        self.assertEqual(self.calc.calculate(), "20")

        self.calc.current_input = "5(2 + 3)"
        self.assertEqual(self.calc.calculate(), "25")

        self.calc.current_input = "(10 + 5"
        self.assertEqual(self.calc.calculate(), "15")

    def test_division_by_zero(self):
        self.calc.current_input = "10 ÷ 0"
        res = self.calc.calculate()
        self.assertEqual(res, "Cannot divide by zero")

        self.calc.current_input = "5 / (2 - 2)"
        res = self.calc.calculate()
        self.assertEqual(res, "Cannot divide by zero")

    def test_invalid_expressions_handled_gracefully(self):
        self.calc.current_input = "5 / * 2"
        res = self.calc.calculate()
        self.assertEqual(res, "Invalid expression")

        self.calc.current_input = "()"
        res = self.calc.calculate()
        self.assertEqual(res, "Invalid expression")

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


class TestScientificFunctionsAndModes(unittest.TestCase):
    """
    Dedicated test suite for user scientific requirements:
    - Default mode DEG
    - DEG/RAD switching
    - sin(30) in DEG returns 0.5
    - sin(pi/6) in RAD returns approx 0.5
    - Trigonometric (sin, cos, tan)
    - Inverse trigonometric (asin, acos, atan)
    - Logarithmic (log10, ln)
    - Other: sqrt, power, factorial, absolute value, exp, pi, e
    - Safe domain error handling
    """

    def setUp(self):
        self.calc = CalculatorEngine()

    def test_default_mode_is_deg(self):
        self.assertEqual(self.calc.angle_mode, "DEG")

    def test_switch_between_deg_and_rad(self):
        self.calc.set_angle_mode("RAD")
        self.assertEqual(self.calc.angle_mode, "RAD")
        self.calc.toggle_angle_mode()
        self.assertEqual(self.calc.angle_mode, "DEG")
        self.calc.toggle_angle_mode()
        self.assertEqual(self.calc.angle_mode, "RAD")

    def test_sin_30_in_deg_returns_0_5(self):
        self.calc.set_angle_mode("DEG")
        self.calc.current_input = "sin(30)"
        res = self.calc.calculate()
        self.assertEqual(res, "0.5")

    def test_sin_pi_over_6_in_rad_returns_0_5(self):
        self.calc.set_angle_mode("RAD")
        self.calc.current_input = "sin(pi / 6)"
        res = self.calc.calculate()
        self.assertEqual(res, "0.5")

    def test_trigonometric_cos_and_tan(self):
        self.calc.set_angle_mode("DEG")
        self.calc.current_input = "cos(60)"
        self.assertEqual(self.calc.calculate(), "0.5")

        self.calc.current_input = "tan(45)"
        self.assertEqual(self.calc.calculate(), "1")

    def test_inverse_trigonometric(self):
        self.calc.set_angle_mode("DEG")
        self.calc.current_input = "asin(0.5)"
        self.assertEqual(self.calc.calculate(), "30")

        self.calc.current_input = "acos(0.5)"
        self.assertEqual(self.calc.calculate(), "60")

        self.calc.current_input = "atan(1)"
        self.assertEqual(self.calc.calculate(), "45")

    def test_logarithmic_log10_and_ln(self):
        self.calc.current_input = "log10(100)"
        self.assertEqual(self.calc.calculate(), "2")

        self.calc.current_input = "log(1000)"
        self.assertEqual(self.calc.calculate(), "3")

        self.calc.current_input = "ln(e)"
        self.assertEqual(self.calc.calculate(), "1")

    def test_other_functions_and_constants(self):
        # Square root
        self.calc.current_input = "sqrt(144)"
        self.assertEqual(self.calc.calculate(), "12")

        # Power
        self.calc.current_input = "2 ^ 6"
        self.assertEqual(self.calc.calculate(), "64")

        # Factorial
        self.calc.current_input = "5!"
        self.assertEqual(self.calc.calculate(), "120")

        # Absolute value
        self.calc.current_input = "abs(-25)"
        self.assertEqual(self.calc.calculate(), "25")

        # Exponential e^x
        self.calc.current_input = "exp(0)"
        self.assertEqual(self.calc.calculate(), "1")

        # Constant pi
        self.calc.current_input = "pi"
        res_pi = float(self.calc.calculate())
        self.assertAlmostEqual(res_pi, math.pi, places=8)

        # Constant e
        self.calc.current_input = "e"
        res_e = float(self.calc.calculate())
        self.assertAlmostEqual(res_e, math.e, places=8)

    def test_domain_errors_handled_safely(self):
        # Asin domain error (|x| > 1)
        self.calc.current_input = "asin(2)"
        res = self.calc.calculate()
        self.assertEqual(res, "Math domain error")

        # Acos domain error (|x| > 1)
        self.calc.current_input = "acos(-5)"
        res = self.calc.calculate()
        self.assertEqual(res, "Math domain error")

        # Tan domain error at 90 deg
        self.calc.set_angle_mode("DEG")
        self.calc.current_input = "tan(90)"
        res = self.calc.calculate()
        self.assertEqual(res, "Cannot divide by zero")

        # Log domain error (x <= 0)
        self.calc.current_input = "log10(-10)"
        res = self.calc.calculate()
        self.assertEqual(res, "Math domain error")

        # Ln domain error (x <= 0)
        self.calc.current_input = "ln(0)"
        res = self.calc.calculate()
        self.assertEqual(res, "Math domain error")

        # Sqrt domain error (x < 0)
        self.calc.current_input = "sqrt(-25)"
        res = self.calc.calculate()
        self.assertEqual(res, "Math domain error")


class TestHistoryManager(unittest.TestCase):
    """Unit tests for HistoryManager and its integration with CalculatorEngine."""

    def setUp(self):
        self.test_file = "test_calc_history_temp.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.manager = HistoryManager(storage_file=self.test_file, max_entries=5)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_retrieve_entries(self):
        entry1 = self.manager.add("25 * 4", "100")
        self.assertEqual(entry1.display_text(), "25 * 4 = 100")
        self.assertEqual(len(self.manager.get_all()), 1)

        entry2 = self.manager.add("sin(30)", "0.5")
        entries = self.manager.get_all()
        self.assertEqual(len(entries), 2)
        # Newest calculation should appear first
        self.assertEqual(entries[0].expression, "sin(30)")
        self.assertEqual(entries[1].expression, "25 * 4")
        self.assertEqual(self.manager.get_latest().result, "0.5")

    def test_max_capacity_truncation(self):
        for i in range(10):
            self.manager.add(f"{i} + 1", f"{i + 1}")
        entries = self.manager.get_all()
        self.assertEqual(len(entries), 5)
        # Last added was 9 + 1 = 10
        self.assertEqual(entries[0].expression, "9 + 1")

    def test_clear_history(self):
        self.manager.add("10 + 20", "30")
        self.assertEqual(len(self.manager.get_all()), 1)
        self.manager.clear()
        self.assertEqual(len(self.manager.get_all()), 0)
        self.assertIsNone(self.manager.get_latest())

    def test_delete_entry(self):
        self.manager.add("1 + 1", "2")
        self.manager.add("2 + 2", "4")
        self.assertTrue(self.manager.delete_entry(0))
        entries = self.manager.get_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].expression, "1 + 1")

    def test_file_persistence_save_and_load(self):
        self.manager.add("100 / 4", "25")
        self.assertTrue(os.path.exists(self.test_file))

        # Create new manager loading from same file
        reloaded = HistoryManager(storage_file=self.test_file, max_entries=5)
        entries = reloaded.get_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].expression, "100 / 4")
        self.assertEqual(entries[0].result, "25")

    def test_calculator_engine_records_history(self):
        engine = CalculatorEngine(history_manager=self.manager)
        engine.current_input = "15 * 6"
        res = engine.calculate()
        self.assertEqual(res, "90")
        self.assertEqual(len(self.manager.get_all()), 1)
        self.assertEqual(self.manager.get_latest().expression, "15 * 6")
        self.assertEqual(self.manager.get_latest().result, "90")

        # Unary operation records history
        engine.current_input = "9"
        res_sqrt = engine.apply_unary_operation("sqrt")
        self.assertEqual(res_sqrt, "3")
        self.assertEqual(len(self.manager.get_all()), 2)
        self.assertEqual(self.manager.get_latest().result, "3")


class TestCodeReviewAndEdgeCases(unittest.TestCase):
    """
    Complete testing pass verifying all user-specified checklist items:
    - Basic calculations: 2+3=5, 10-4=6, 5*6=30, 20/4=5
    - Operator precedence: 2+3*4=14, (2+3)*4=20
    - Scientific: sin(30) DEG = 0.5, cos(60) DEG = 0.5, tan(45) DEG = 1,
      sqrt(144) = 12, 2^10 = 1024, 5! = 120, log(100) = 2, ln(e) = 1
    - Edge cases: 10/0, sqrt(-1), log(0), 5.5.5, ((2+3), very large numbers
    - Memory functions & retention
    - Theme switching & persistence
    - Error recovery: continuing calculation normally after error
    """

    def setUp(self):
        self.temp_hist = "test_review_hist_temp.json"
        self.temp_theme = "test_review_theme_temp.json"
        for f in (self.temp_hist, self.temp_theme):
            if os.path.exists(f):
                os.remove(f)
        self.history = HistoryManager(storage_file=self.temp_hist)
        self.calc = CalculatorEngine(history_manager=self.history)

    def tearDown(self):
        for f in (self.temp_hist, self.temp_theme):
            if os.path.exists(f):
                os.remove(f)

    def test_basic_arithmetic_checklist(self):
        # 2+3 = 5
        self.calc.current_input = "2 + 3"
        self.assertEqual(self.calc.calculate(), "5")

        # 10-4 = 6
        self.calc.current_input = "10 - 4"
        self.assertEqual(self.calc.calculate(), "6")

        # 5*6 = 30
        self.calc.current_input = "5 * 6"
        self.assertEqual(self.calc.calculate(), "30")

        # 20/4 = 5
        self.calc.current_input = "20 / 4"
        self.assertEqual(self.calc.calculate(), "5")

    def test_operator_precedence_checklist(self):
        # 2+3*4 = 14
        self.calc.current_input = "2 + 3 * 4"
        self.assertEqual(self.calc.calculate(), "14")

        # (2+3)*4 = 20
        self.calc.current_input = "(2 + 3) * 4"
        self.assertEqual(self.calc.calculate(), "20")

    def test_scientific_checklist(self):
        # sin(30) DEG = 0.5
        self.calc.set_angle_mode("DEG")
        self.calc.current_input = "sin(30)"
        self.assertEqual(self.calc.calculate(), "0.5")

        # cos(60) DEG = 0.5
        self.calc.current_input = "cos(60)"
        self.assertEqual(self.calc.calculate(), "0.5")

        # tan(45) DEG = 1
        self.calc.current_input = "tan(45)"
        self.assertEqual(self.calc.calculate(), "1")

        # sqrt(144) = 12
        self.calc.current_input = "sqrt(144)"
        self.assertEqual(self.calc.calculate(), "12")

        # 2^10 = 1024
        self.calc.current_input = "2 ^ 10"
        self.assertEqual(self.calc.calculate(), "1024")

        # 5! = 120
        self.calc.current_input = "5!"
        self.assertEqual(self.calc.calculate(), "120")

        # log(100) = 2
        self.calc.current_input = "log(100)"
        self.assertEqual(self.calc.calculate(), "2")

        # ln(e) = 1
        self.calc.current_input = "ln(e)"
        self.assertEqual(self.calc.calculate(), "1")

        # log(8, 2) custom base = 3
        self.calc.current_input = "log(8, 2)"
        self.assertEqual(self.calc.calculate(), "3")

        # cosh(0) = 1
        self.calc.current_input = "cosh(0)"
        self.assertEqual(self.calc.calculate(), "1")

        # cbrt unary
        self.calc.current_input = "27"
        self.assertEqual(self.calc.apply_unary_operation("cbrt"), "3")

        # scientific notation: 2e3 + 500 = 2500
        self.calc.current_input = "2e3 + 500"
        self.assertEqual(self.calc.calculate(), "2500")

    def test_edge_cases_checklist(self):
        # 10/0 -> "Cannot divide by zero"
        self.calc.current_input = "10 / 0"
        self.assertEqual(self.calc.calculate(), "Cannot divide by zero")

        # sqrt(-1) -> "Math domain error"
        self.calc.current_input = "sqrt(-1)"
        self.assertEqual(self.calc.calculate(), "Math domain error")

        # log(0) -> "Math domain error"
        self.calc.current_input = "log(0)"
        self.assertEqual(self.calc.calculate(), "Math domain error")

        # 5.5.5 -> "Invalid expression"
        self.calc.current_input = "5.5.5"
        self.assertEqual(self.calc.calculate(), "Invalid expression")

        # ((2+3) -> auto balances unclosed parentheses -> 5
        self.calc.current_input = "((2 + 3)"
        self.assertEqual(self.calc.calculate(), "5")

        # very large numbers -> scientific notation or overflow
        self.calc.current_input = "2 ^ 100"
        res = self.calc.calculate()
        self.assertTrue("e+" in res or len(res) > 20)

        self.calc.current_input = "10 ^ 500"
        self.assertEqual(self.calc.calculate(), "Overflow: Result too large")

    def test_error_recovery(self):
        # Trigger division by zero error
        self.calc.current_input = "10 / 0"
        res = self.calc.calculate()
        self.assertEqual(res, "Cannot divide by zero")
        self.assertTrue(self.calc.is_error)

        # Typing a new number immediately clears error and begins fresh calculation
        self.calc.append_number("8")
        self.assertEqual(self.calc.current_input, "8")
        self.assertFalse(self.calc.is_error)

        self.calc.append_operator("+")
        self.calc.append_number("2")
        self.assertEqual(self.calc.calculate(), "10")

    def test_memory_functions_full_flow(self):
        # Initially empty memory
        self.assertFalse(self.calc.has_memory)

        # MS: store 42
        self.calc.current_input = "42"
        self.calc.memory_store()
        self.assertTrue(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 42.0)

        # M+: add 8 -> 50
        self.calc.current_input = "8"
        self.calc.memory_add()
        self.assertEqual(self.calc.memory_value, 50.0)

        # M-: subtract 20 -> 30
        self.calc.current_input = "20"
        self.calc.memory_subtract()
        self.assertEqual(self.calc.memory_value, 30.0)

        # MR: recall 30
        self.calc.current_input = "0"
        self.calc.memory_recall()
        self.assertEqual(self.calc.current_input, "30")

        # MC: clear memory
        self.calc.memory_clear()
        self.assertFalse(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 0.0)

    def test_theme_persistence_and_restart(self):
        from theme import ThemeManager
        tm = ThemeManager(settings_file=self.temp_theme, initial_mode="dark")
        self.assertEqual(tm.current_mode, "dark")

        # Toggle to light
        new_mode = tm.toggle()
        self.assertEqual(new_mode, "light")

        # Simulate restart by instantiating new ThemeManager with same file
        reloaded_tm = ThemeManager(settings_file=self.temp_theme)
        self.assertEqual(reloaded_tm.current_mode, "light")


class TestStandardCalculatorMode(unittest.TestCase):
    """
    Unit tests specifically validating the Standard Calculator Mode:
    - Addition, subtraction, multiplication, division
    - Operator precedence (PEMDAS)
    - Parentheses (nested, implicit multiplication, auto-balancing)
    - Percentage operations (unary % and expression %)
    - Decimal numbers and duplicate dot prevention
    - Sign change (±) and negative numbers
    - Division by zero and error recovery
    - Memory operations (MC, MR, M+, M-, MS)
    - Calculation history logging
    - Clear (C, CE) and backspace (DEL)
    """

    def setUp(self):
        self.temp_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_hist = os.path.join(self.temp_dir, "test_standard_hist.json")
        self.history = HistoryManager(storage_file=self.temp_hist)
        self.calc = CalculatorEngine(history_manager=self.history)

    def tearDown(self):
        if os.path.exists(self.temp_hist):
            try:
                os.remove(self.temp_hist)
            except Exception:
                pass

    def test_basic_arithmetic_operations(self):
        # Addition
        self.calc.current_input = "12.5 + 7.5"
        self.assertEqual(self.calc.calculate(), "20")

        # Subtraction
        self.calc.current_input = "100 - 45.5"
        self.assertEqual(self.calc.calculate(), "54.5")

        # Multiplication
        self.calc.current_input = "15 * 6"
        self.assertEqual(self.calc.calculate(), "90")

        # Division
        self.calc.current_input = "144 / 12"
        self.assertEqual(self.calc.calculate(), "12")

        # Fractional division
        self.calc.current_input = "7 / 2"
        self.assertEqual(self.calc.calculate(), "3.5")

    def test_operator_precedence_pemdas(self):
        # Multiplication before addition: 2 + 3 * 4 = 14
        self.calc.current_input = "2 + 3 * 4"
        self.assertEqual(self.calc.calculate(), "14")

        # Division before subtraction: 10 - 6 / 2 = 7
        self.calc.current_input = "10 - 6 / 2"
        self.assertEqual(self.calc.calculate(), "7")

        # Left-to-right division and multiplication: 20 / 4 * 2 = 10
        self.calc.current_input = "20 / 4 * 2"
        self.assertEqual(self.calc.calculate(), "10")

        # Complex precedence: 100 - 50 / 2 + 10 = 85
        self.calc.current_input = "100 - 50 / 2 + 10"
        self.assertEqual(self.calc.calculate(), "85")

    def test_parentheses_and_grouping(self):
        # Parentheses override precedence: (2 + 3) * 4 = 20
        self.calc.current_input = "(2 + 3) * 4"
        self.assertEqual(self.calc.calculate(), "20")

        # Nested parentheses: ((5 + 3) * 2) - 6 = 10
        self.calc.current_input = "((5 + 3) * 2) - 6"
        self.assertEqual(self.calc.calculate(), "10")

        # Parentheses in denominator: 30 / (2 + 3) = 6
        self.calc.current_input = "30 / (2 + 3)"
        self.assertEqual(self.calc.calculate(), "6")

        # Implicit multiplication: 5(2 + 3) = 25
        self.calc.current_input = "5(2 + 3)"
        self.assertEqual(self.calc.calculate(), "25")

        # Auto-balancing unclosed open parentheses: (10 + 5 * 2 = 20
        self.calc.current_input = "(10 + 5 * 2"
        self.assertEqual(self.calc.calculate(), "20")

    def test_percentage_operations(self):
        # Unary percentage button operation (x / 100)
        self.calc.current_input = "50"
        res = self.calc.apply_unary_operation("percent")
        self.assertEqual(res, "0.5")
        self.assertEqual(self.calc.previous_expression, "50%")

        self.calc.current_input = "250"
        res = self.calc.apply_unary_operation("percent")
        self.assertEqual(res, "2.5")

        # Percentage inside expression: 200 * 10% = 20
        self.calc.current_input = "200 * 10%"
        self.assertEqual(self.calc.calculate(), "20")

    def test_decimal_numbers_and_validation(self):
        # Decimal addition
        self.calc.current_input = "0.1 + 0.2"
        self.assertEqual(self.calc.calculate(), "0.3")

        # Keypad decimal entry
        self.calc.clear()
        self.calc.append_decimal()  # Starts as '0.'
        self.assertEqual(self.calc.current_input, "0.")
        self.calc.append_number("7")
        self.assertEqual(self.calc.current_input, "0.7")

        # Multiple decimals in single operand prevented
        self.calc.append_decimal()
        self.assertEqual(self.calc.current_input, "0.7")

        # Invalid multiple dots in expression string
        self.calc.current_input = "5.5.5"
        self.assertEqual(self.calc.calculate(), "Invalid expression")

    def test_negative_numbers_and_sign_change(self):
        # Sign toggle on positive integer
        self.calc.current_input = "42"
        self.calc.toggle_sign()
        self.assertEqual(self.calc.current_input, "-42")

        # Sign toggle on negative number
        self.calc.toggle_sign()
        self.assertEqual(self.calc.current_input, "42")

        # Expression with negative operand: -8 + 15 = 7
        self.calc.current_input = "-8 + 15"
        self.assertEqual(self.calc.calculate(), "7")

        # Multiplication with negative number: 5 * (-3) = -15
        self.calc.current_input = "5 * (-3)"
        self.assertEqual(self.calc.calculate(), "-15")

    def test_division_by_zero_and_recovery(self):
        self.calc.current_input = "100 / 0"
        self.assertEqual(self.calc.calculate(), "Cannot divide by zero")
        self.assertTrue(self.calc.is_error)

        # Immediate recovery on next digit input
        self.calc.append_number("9")
        self.assertEqual(self.calc.current_input, "9")
        self.assertFalse(self.calc.is_error)

        self.calc.append_operator("+")
        self.calc.append_number("1")
        self.assertEqual(self.calc.calculate(), "10")

    def test_clear_and_backspace_behaviors(self):
        # DEL / Backspace
        self.calc.current_input = "12345"
        self.calc.backspace()
        self.assertEqual(self.calc.current_input, "1234")

        # Backspace down to zero
        self.calc.current_input = "9"
        self.calc.backspace()
        self.assertEqual(self.calc.current_input, "0")

        # CE / Clear input
        self.calc.current_input = "999"
        self.calc.clear()
        self.assertEqual(self.calc.current_input, "0")

        # C / All Clear: clears input and previous expression
        self.calc.current_input = "50"
        self.calc.previous_expression = "25 * 2 ="
        self.calc.all_clear()
        self.assertEqual(self.calc.current_input, "0")
        self.assertEqual(self.calc.previous_expression, "")

    def test_memory_operations_standard_flow(self):
        # Initial empty state
        self.assertFalse(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 0.0)

        # MS (Store): store 120
        self.calc.current_input = "120"
        self.assertTrue(self.calc.memory_store())
        self.assertTrue(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 120.0)

        # M+ (Add): add 30 -> 150
        self.calc.current_input = "30"
        self.assertTrue(self.calc.memory_add())
        self.assertEqual(self.calc.memory_value, 150.0)

        # M- (Subtract): subtract 50 -> 100
        self.calc.current_input = "50"
        self.assertTrue(self.calc.memory_subtract())
        self.assertEqual(self.calc.memory_value, 100.0)

        # MR (Recall): recall into fresh calculation
        self.calc.clear()
        self.assertEqual(self.calc.memory_recall(), "100")

        # MC (Clear): reset memory
        self.calc.memory_clear()
        self.assertFalse(self.calc.has_memory)
        self.assertEqual(self.calc.memory_value, 0.0)

    def test_calculation_history_standard_flow(self):
        self.calc.current_input = "25 * 4"
        self.assertEqual(self.calc.calculate(), "100")

        entries = self.history.get_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].expression, "25 * 4")
        self.assertEqual(entries[0].result, "100")

        # Perform second calculation
        self.calc.current_input = "(10 + 20) / 2"
        self.assertEqual(self.calc.calculate(), "15")

        entries = self.history.get_all()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].expression, "(10 + 20) / 2")
        self.assertEqual(entries[0].result, "15")


if __name__ == "__main__":
    unittest.main()



