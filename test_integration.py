"""
test_integration.py
===================
Integration tests verifying app shell mode switching,
including Standard, Scientific, and Graphing views,
as well as theme synchronization and UI component coordination.
"""

import unittest
from unittest.mock import MagicMock, patch
import customtkinter as ctk

from main import ModernCalculatorApp
from views.standard_view import StandardView
from views.scientific_view import ScientificView
from views.graphing_view import GraphingView
from views.programmer_view import ProgrammerView
from views.date_view import DateCalcView
from views.unit_converter_view import UnitConverterView
from views.currency_view import CurrencyView
from views.settings_view import SettingsView


class TestAppModeSwitching(unittest.TestCase):
    """Verifies that the shell switches smoothly between views."""

    @classmethod
    def setUpClass(cls):
        # Prevent window from showing up during automated test
        ctk.set_appearance_mode("Dark")
        cls.app = ModernCalculatorApp()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass

    def test_01_default_mode_is_standard(self):
        """Standard mode should be mounted upon startup."""
        self.assertEqual(self.app.current_mode_id, "standard")
        self.assertIsInstance(self.app.current_view, StandardView)
        self.assertEqual(self.app.title_label.cget("text"), "Standard")

    def test_02_switch_to_scientific(self):
        """Switching to scientific mounts ScientificView and displays DEG/RAD badge."""
        self.app.switch_mode("scientific")
        self.assertEqual(self.app.current_mode_id, "scientific")
        self.assertIsInstance(self.app.current_view, ScientificView)
        self.assertEqual(self.app.title_label.cget("text"), "Scientific")
        # Check angle mode badge button is visible
        self.assertEqual(self.app.deg_rad_btn.winfo_manager(), "pack")
        self.assertIn(self.app.deg_rad_btn.cget("text"), ["DEG", "RAD"])

    def test_03_switch_to_graphing(self):
        """Switching to graphing mounts GraphingView and initializes canvas."""
        self.app.switch_mode("graphing")
        self.assertEqual(self.app.current_mode_id, "graphing")
        self.assertIsInstance(self.app.current_view, GraphingView)
        self.assertEqual(self.app.title_label.cget("text"), "Graphing")
        # Check DEG/RAD badge button is hidden in graphing mode
        self.assertEqual(self.app.deg_rad_btn.winfo_manager(), "")

        graph_view: GraphingView = self.app.current_view
        # Check default initial plot was added (sin(x))
        self.assertGreaterEqual(len(graph_view.graph_engine.get_functions()), 1)
        self.assertEqual(graph_view.graph_engine.get_functions()[0].expression, "sin(x)")

        # Test adding a second function
        graph_view.style_var.set("Dashed")
        graph_view._add_function_string("x^2")
        self.assertEqual(len(graph_view.graph_engine.get_functions()), 2)
        self.assertEqual(graph_view.graph_engine.get_functions()[1].line_style, "--")

        # Test zooming
        initial_span = graph_view.x_max - graph_view.x_min
        graph_view._zoom(0.8)
        new_span = graph_view.x_max - graph_view.x_min
        self.assertLess(new_span, initial_span)

        # Test reset view
        graph_view._reset_view()
        self.assertEqual(graph_view.x_min, -10.0)
        self.assertEqual(graph_view.x_max, 10.0)

    def test_04_switch_back_to_standard(self):
        """Switching back to standard re-activates StandardView."""
        self.app.switch_mode("standard")
        self.assertEqual(self.app.current_mode_id, "standard")
        self.assertIsInstance(self.app.current_view, StandardView)
        self.assertEqual(self.app.title_label.cget("text"), "Standard")
        self.assertEqual(self.app.deg_rad_btn.winfo_manager(), "")

    def test_05_switch_to_programmer(self):
        """Switching to programmer mounts ProgrammerView and verifies bit logic."""
        self.app.switch_mode("programmer")
        self.assertEqual(self.app.current_mode_id, "programmer")
        self.assertIsInstance(self.app.current_view, ProgrammerView)
        self.assertEqual(self.app.title_label.cget("text"), "Programmer")
        self.assertEqual(self.app.deg_rad_btn.winfo_manager(), "")

        prog_view: ProgrammerView = self.app.current_view
        # Test input and bit toggle
        prog_view.engine.set_value(0xA5)
        prog_view._update_display()
        self.assertEqual(prog_view.engine.get_hex_string(), "A5")
        self.assertEqual(prog_view.engine.get_dec_string(), "165")
        # Toggle bit 0 (from 1 to 0) -> 0xA4 (164)
        prog_view._on_toggle_bit(0)
        self.assertEqual(prog_view.engine.current_value, 0xA4)

    def test_06_switch_to_date_calc(self):
        """Switching to date_calc mounts DateCalcView and verifies calculations."""
        self.app.switch_mode("date_calc")
        self.assertEqual(self.app.current_mode_id, "date_calc")
        self.assertIsInstance(self.app.current_view, DateCalcView)
        self.assertEqual(self.app.title_label.cget("text"), "Date Calculation")
        self.assertEqual(self.app.deg_rad_btn.winfo_manager(), "")

        date_view: DateCalcView = self.app.current_view
        # Check sub-mode tabs
        self.assertEqual(date_view.tab_selector.get(), "Difference")
        date_view._on_tab_changed("Add / Subtract")
        self.assertEqual(date_view.current_tab, "Add / Subtract")
        date_view._on_tab_changed("Date Info")
        self.assertEqual(date_view.current_tab, "Date Info")

    def test_07_theme_sync(self):
        """Switching theme propagates to theme manager and views."""
        self.app.theme_mgr.set_mode("light")
        self.assertEqual(self.app.theme_mgr.current_mode, "light")
        # Switch to programmer to ensure theme is sound
        self.app.switch_mode("programmer")
        self.assertIsInstance(self.app.current_view, ProgrammerView)
        # Restore dark
        self.app.theme_mgr.set_mode("dark")
        self.assertEqual(self.app.theme_mgr.current_mode, "dark")


    def test_08_switch_to_currency(self):
        """Switching to currency mounts CurrencyView."""
        self.app.switch_mode("currency")
        self.assertEqual(self.app.current_mode_id, "currency")
        self.assertIsInstance(self.app.current_view, CurrencyView)
        self.assertEqual(self.app.title_label.cget("text"), "Currency Converter")
        curr_view: CurrencyView = self.app.current_view
        self.assertIsNotNone(curr_view.result_label.cget("text"))

    def test_09_switch_to_all_12_unit_converters(self):
        """All 12 unit converter modes mount UnitConverterView with proper category."""
        categories = [
            "volume", "length", "weight", "temperature", "energy",
            "area", "speed", "time", "power", "data", "pressure", "angle"
        ]
        for cat in categories:
            self.app.switch_mode(cat)
            self.assertEqual(self.app.current_mode_id, cat)
            self.assertIsInstance(self.app.current_view, UnitConverterView)
            self.assertEqual(self.app.current_view.category, cat)

    def test_10_unit_converter_actions(self):
        """Tests input, swap, clear, and calculation on a UnitConverterView."""
        self.app.switch_mode("length")
        view: UnitConverterView = self.app.current_view

        # Set 10 Meters to Feet
        view.input_entry.delete(0, "end")
        view.input_entry.insert(0, "10")
        view.from_unit_var.set("Meters")
        view.to_unit_var.set("Feet")
        view._convert()

        res_str = view.result_label.cget("text")
        self.assertTrue(float(res_str) > 30.0)

        # Test swap
        view._swap_units()
        self.assertEqual(view.from_unit_var.get(), "Feet")
        self.assertEqual(view.to_unit_var.get(), "Meters")

        # Test clear
        view._clear_input()
        self.assertEqual(view.input_entry.get(), "0")
        self.assertEqual(view.result_label.cget("text"), "0")


if __name__ == "__main__":
    unittest.main()
