"""
test_graphing.py
================
Unit tests for GraphingEngine:
- Expression cleaning and implicit multiplication
- Safe AST validation (rejection of malicious/arbitrary code)
- Vectorized function evaluation (x^2, sin(x), cos(x), log(x), sqrt(x))
- Undefined domains (sqrt(x) for x < 0, log(x) for x <= 0)
- Discontinuity and asymptote detection (tan(x), 1/x)
- Multi-function management (add, toggle, style, remove, clear)
"""

import unittest
import numpy as np

from graphing_engine import GraphingEngine, PlotFunction


class TestGraphingEngine(unittest.TestCase):

    def setUp(self):
        self.engine = GraphingEngine()

    def test_clean_expression(self):
        # Strip 'y =' and 'f(x) ='
        self.assertEqual(GraphingEngine.clean_expression("y = x^2"), "x**2")
        self.assertEqual(GraphingEngine.clean_expression("f(x) = sin(x)"), "sin(x)")
        self.assertEqual(GraphingEngine.clean_expression("Y=2x+1"), "2 * x+1")

        # Implicit multiplication
        self.assertEqual(GraphingEngine.clean_expression("2x"), "2 * x")
        self.assertEqual(GraphingEngine.clean_expression("3(x+1)"), "3 * (x+1)")
        self.assertEqual(GraphingEngine.clean_expression("x(x-1)"), "x * (x-1)")
        self.assertEqual(GraphingEngine.clean_expression("(x+1)(x-1)"), "(x+1) * (x-1)")

        # Math symbols conversion
        self.assertEqual(GraphingEngine.clean_expression("√x"), "sqrt(x)")
        self.assertEqual(GraphingEngine.clean_expression("|x|"), "abs(x)")

        # Auto-balancing unclosed parentheses
        self.assertEqual(GraphingEngine.clean_expression("(x + 2"), "(x + 2)")

        # Empty expression
        with self.assertRaises(ValueError):
            GraphingEngine.clean_expression("   ")
        with self.assertRaises(ValueError):
            GraphingEngine.clean_expression("y = ")

    def test_ast_safety_validation(self):
        # Valid standard expressions
        valid_expressions = [
            "x**2",
            "sin(x)",
            "cos(x)",
            "tan(x)",
            "log(x)",
            "ln(x)",
            "sqrt(x)",
            "cbrt(x)",
            "exp(x)",
            "abs(x)",
            "sinh(x)",
            "cosh(x)",
            "tanh(x)",
            "log(x, 2)",
            "2 * pi * x",
        ]
        for expr in valid_expressions:
            tree = GraphingEngine.validate_ast(expr)
            self.assertIsNotNone(tree)

        # Invalid or unsafe expressions
        unsafe_expressions = [
            "__import__('os').system('dir')",
            "open('test.txt')",
            "exec('pass')",
            "eval('5')",
            "lambda x: x",
            "x.attr",
            "x[0]",
            "unknown_var + 1",
            "bad_func(x)",
        ]
        for expr in unsafe_expressions:
            with self.assertRaises(ValueError):
                GraphingEngine.validate_ast(expr)

    def test_parabola_evaluation(self):
        # y = x^2
        x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        y, err = GraphingEngine.evaluate_function("x^2", x)
        self.assertIsNone(err)
        np.testing.assert_allclose(y, [4.0, 1.0, 0.0, 1.0, 4.0])

    def test_trigonometric_evaluation(self):
        # y = sin(x)
        x = np.array([0.0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
        y, err = GraphingEngine.evaluate_function("sin(x)", x)
        self.assertIsNone(err)
        np.testing.assert_allclose(y, [0.0, 1.0, 0.0, -1.0, 0.0], atol=1e-7)

        # y = cos(x)
        y_cos, err = GraphingEngine.evaluate_function("cos(x)", x)
        self.assertIsNone(err)
        np.testing.assert_allclose(y_cos, [1.0, 0.0, -1.0, 0.0, 1.0], atol=1e-7)

    def test_undefined_domain_sqrt(self):
        # y = sqrt(x) - negative values should be masked as NaN
        x = np.array([-4.0, -1.0, 0.0, 4.0, 9.0])
        y, err = GraphingEngine.evaluate_function("sqrt(x)", x)
        self.assertIsNone(err)
        self.assertTrue(np.isnan(y[0]))
        self.assertTrue(np.isnan(y[1]))
        self.assertEqual(y[2], 0.0)
        self.assertEqual(y[3], 2.0)
        self.assertEqual(y[4], 3.0)

    def test_undefined_domain_log(self):
        # y = log(x) - x <= 0 should be NaN
        x = np.array([-2.0, 0.0, 1.0, np.e])
        y, err = GraphingEngine.evaluate_function("ln(x)", x)
        self.assertIsNone(err)
        self.assertTrue(np.isnan(y[0]))
        self.assertTrue(np.isnan(y[1]))
        self.assertAlmostEqual(y[2], 0.0)
        self.assertAlmostEqual(y[3], 1.0)

    def test_discontinuity_detection(self):
        # y = 1/x at x = 0
        x = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
        y, err = GraphingEngine.evaluate_function("1/x", x)
        self.assertIsNone(err)
        self.assertTrue(np.isnan(y[2]))  # x=0 -> NaN

    def test_multi_function_management(self):
        # Add functions
        fn1, err1 = self.engine.add_function("y = sin(x)", line_style="-")
        self.assertIsNone(err1)
        self.assertIsNotNone(fn1)
        self.assertEqual(fn1.clean_expr, "sin(x)")

        fn2, err2 = self.engine.add_function("x^2", line_style="--")
        self.assertIsNone(err2)
        self.assertIsNotNone(fn2)

        funcs = self.engine.get_functions()
        self.assertEqual(len(funcs), 2)
        self.assertEqual(funcs[0].color, GraphingEngine.COLOR_PALETTE[0])
        self.assertEqual(funcs[1].color, GraphingEngine.COLOR_PALETTE[1])

        # Toggle visibility
        self.engine.toggle_visibility(fn1.id)
        self.assertFalse(funcs[0].visible)
        self.engine.toggle_visibility(fn1.id)
        self.assertTrue(funcs[0].visible)

        # Change line style
        self.engine.set_line_style(fn1.id, ":")
        self.assertEqual(funcs[0].line_style, ":")

        # Remove function
        self.assertTrue(self.engine.remove_function(fn1.id))
        self.assertEqual(len(self.engine.get_functions()), 1)

        # Clear functions
        self.engine.clear_functions()
        self.assertEqual(len(self.engine.get_functions()), 0)


if __name__ == "__main__":
    unittest.main()
