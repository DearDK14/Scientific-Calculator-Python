"""
test_date_calc.py
=================
Unit tests for Date Calculation Engine (date_engine.py).
Validates date difference, addition, subtraction, leap year handling,
and calendar metadata.
"""

from datetime import date
import unittest
from date_engine import DateEngine


class TestDateEngine(unittest.TestCase):
    """Exhaustive test suite for DateEngine."""

    # -------------------------------------------------------------------------
    # 1. Validation & Parsing
    # -------------------------------------------------------------------------
    def test_valid_and_invalid_date_parts(self):
        # Valid date
        valid, dt, err = DateEngine.validate_date_parts(2026, 9, 22)
        self.assertTrue(valid)
        self.assertEqual(dt, date(2026, 9, 22))
        self.assertIsNone(err)

        # Invalid month
        valid, _, err = DateEngine.validate_date_parts(2026, 13, 1)
        self.assertFalse(valid)
        self.assertIn("Month must be between 1 and 12", err)

        # Invalid day for 30-day month (April 31)
        valid, _, err = DateEngine.validate_date_parts(2026, 4, 31)
        self.assertFalse(valid)
        self.assertIn("April 2026 has 30 days", err)

        # Feb 29 in non-leap year (2026)
        valid, _, err = DateEngine.validate_date_parts(2026, 2, 29)
        self.assertFalse(valid)
        self.assertIn("not a leap year", err)

        # Feb 29 in leap year (2024)
        valid, dt, _ = DateEngine.validate_date_parts(2024, 2, 29)
        self.assertTrue(valid)
        self.assertEqual(dt, date(2024, 2, 29))

    # -------------------------------------------------------------------------
    # 2. Date Difference Calculation
    # -------------------------------------------------------------------------
    def test_date_difference_same_day(self):
        d1 = date(2026, 5, 10)
        res = DateEngine.calculate_date_difference(d1, d1)
        self.assertEqual(res.total_days, 0)
        self.assertEqual(res.weeks, 0)
        self.assertEqual(res.years, 0)
        self.assertEqual(res.months, 0)
        self.assertEqual(res.days, 0)
        self.assertFalse(res.is_negative)

    def test_date_difference_weeks_and_days(self):
        d1 = date(2026, 1, 1)
        d2 = date(2026, 1, 18)  # 17 days = 2 weeks, 3 days
        res = DateEngine.calculate_date_difference(d1, d2)
        self.assertEqual(res.total_days, 17)
        self.assertEqual(res.weeks, 2)
        self.assertEqual(res.remaining_days_in_week, 3)

    def test_date_difference_calendar_breakdown(self):
        # 1 year, 2 months, 5 days
        d1 = date(2025, 1, 10)
        d2 = date(2026, 3, 15)
        res = DateEngine.calculate_date_difference(d1, d2)
        self.assertEqual(res.years, 1)
        self.assertEqual(res.months, 2)
        self.assertEqual(res.days, 5)
        self.assertFalse(res.is_negative)

    def test_date_difference_reverse_order(self):
        d1 = date(2026, 12, 25)
        d2 = date(2026, 1, 1)
        res = DateEngine.calculate_date_difference(d1, d2)
        self.assertTrue(res.is_negative)
        self.assertEqual(res.total_days, 358)
        self.assertIn("Earlier by", res.summary_text())

    # -------------------------------------------------------------------------
    # 3. Add or Subtract Days, Months, and Years
    # -------------------------------------------------------------------------
    def test_add_days(self):
        start = date(2026, 1, 1)
        success, res, _ = DateEngine.add_subtract_date(start, days=45, operation="add")
        self.assertTrue(success)
        self.assertEqual(res.resulting_date, date(2026, 2, 15))

    def test_subtract_days(self):
        start = date(2026, 3, 1)
        success, res, _ = DateEngine.add_subtract_date(start, days=1, operation="subtract")
        self.assertTrue(success)
        # 2026 is non-leap, so March 1 minus 1 day is Feb 28
        self.assertEqual(res.resulting_date, date(2026, 2, 28))

    def test_add_months_with_clipping(self):
        # Jan 31 + 1 month in non-leap year (2026) -> Feb 28
        start = date(2026, 1, 31)
        success, res, _ = DateEngine.add_subtract_date(start, months=1, operation="add")
        self.assertTrue(success)
        self.assertEqual(res.resulting_date, date(2026, 2, 28))

        # Jan 31 + 1 month in leap year (2024) -> Feb 29
        start_leap = date(2024, 1, 31)
        success, res, _ = DateEngine.add_subtract_date(start_leap, months=1, operation="add")
        self.assertTrue(success)
        self.assertEqual(res.resulting_date, date(2024, 2, 29))

    def test_add_years_and_months(self):
        start = date(2026, 6, 15)
        success, res, _ = DateEngine.add_subtract_date(start, years=2, months=3, days=5, operation="add")
        self.assertTrue(success)
        self.assertEqual(res.resulting_date, date(2028, 9, 20))

    # -------------------------------------------------------------------------
    # 4. Date Information
    # -------------------------------------------------------------------------
    def test_date_info_leap_year(self):
        # 2024 is leap
        info_2024 = DateEngine.get_date_info(date(2024, 6, 1))
        self.assertTrue(info_2024.is_leap_year)
        self.assertEqual(info_2024.total_days_in_year, 366)

        # 2026 is non-leap
        info_2026 = DateEngine.get_date_info(date(2026, 6, 1))
        self.assertFalse(info_2026.is_leap_year)
        self.assertEqual(info_2026.total_days_in_year, 365)

    def test_date_info_metrics(self):
        d = date(2026, 1, 1)  # Thursday
        info = DateEngine.get_date_info(d)
        self.assertEqual(info.day_of_week, "Thursday")
        self.assertEqual(info.day_of_year, 1)
        self.assertEqual(info.days_remaining_in_year, 364)
        self.assertEqual(info.quarter, 1)
        self.assertEqual(info.week_number, 1)

        # Last day of year
        d_end = date(2026, 12, 31)
        info_end = DateEngine.get_date_info(d_end)
        self.assertEqual(info_end.days_remaining_in_year, 0)
        self.assertEqual(info_end.quarter, 4)


if __name__ == "__main__":
    unittest.main()
