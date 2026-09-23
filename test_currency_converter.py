"""
test_currency_converter.py
==========================
Unit tests for Currency Converter Engine and Providers.
"""

import os
import tempfile
import unittest
from currency_provider import (
    CurrencyEngine,
    ExchangeRateProvider,
    MockExchangeRateProvider,
)


class FailingProvider(ExchangeRateProvider):
    """Simulates network timeout/failure."""
    def fetch_rates(self, base_currency: str = "USD"):
        return False, {}, "Connection timed out"


class TestCurrencyConverter(unittest.TestCase):
    """Exhaustive tests for currency conversions, mock rates, and caching."""

    def setUp(self):
        self.mock_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "INR": 80.0,
            "GBP": 0.75,
            "JPY": 110.0,
        }
        self.mock_provider = MockExchangeRateProvider(self.mock_rates)
        self.temp_cache = tempfile.NamedTemporaryFile(delete=False)
        self.temp_cache.close()
        self.engine = CurrencyEngine(provider=self.mock_provider, cache_file=self.temp_cache.name)
        self.engine.refresh_rates()

    def tearDown(self):
        if os.path.exists(self.temp_cache.name):
            try:
                os.remove(self.temp_cache.name)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # 1. Conversion Math
    # -------------------------------------------------------------------------
    def test_direct_usd_conversions(self):
        # 100 USD -> INR = 8000.0
        ok, res, rate, err = self.engine.convert(100.0, "USD", "INR")
        self.assertTrue(ok)
        self.assertEqual(res, 8000.0)
        self.assertEqual(rate, 80.0)
        self.assertIsNone(err)

        # 100 USD -> EUR = 85.0
        ok, res, rate, _ = self.engine.convert(100.0, "USD", "EUR")
        self.assertTrue(ok)
        self.assertEqual(res, 85.0)
        self.assertEqual(rate, 0.85)

    def test_cross_currency_conversions(self):
        # 85 EUR -> USD = 100.0
        ok, res, rate, _ = self.engine.convert(85.0, "EUR", "USD")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 100.0, places=4)

        # EUR to INR: 85 EUR -> 8000 INR (1 EUR = 80 / 0.85 approx 94.1176 INR)
        ok, res, rate, _ = self.engine.convert(85.0, "EUR", "INR")
        self.assertTrue(ok)
        self.assertAlmostEqual(res, 8000.0, places=4)

    def test_identity_and_zero_amount(self):
        ok, res, rate, _ = self.engine.convert(50.0, "USD", "USD")
        self.assertTrue(ok)
        self.assertEqual(res, 50.0)
        self.assertEqual(rate, 1.0)

        ok, res, rate, _ = self.engine.convert(0.0, "USD", "EUR")
        self.assertTrue(ok)
        self.assertEqual(res, 0.0)

    def test_negative_amount_rejected(self):
        ok, res, rate, err = self.engine.convert(-10.0, "USD", "INR")
        self.assertFalse(ok)
        self.assertIn("cannot be negative", err)

    def test_rate_formula(self):
        formula = self.engine.get_rate_formula("USD", "INR")
        self.assertEqual(formula, "1 USD = 80 INR")

    # -------------------------------------------------------------------------
    # 2. Offline Fallback & Labeling
    # -------------------------------------------------------------------------
    def test_failing_provider_falls_back_to_cache(self):
        failing_engine = CurrencyEngine(provider=FailingProvider(), cache_file=self.temp_cache.name)
        success, msg = failing_engine.refresh_rates()
        # Must gracefully fall back without crashing
        self.assertFalse(success)
        self.assertFalse(failing_engine.is_live)
        # Verify it labels offline/cached rates clearly
        self.assertTrue(
            "Offline" in failing_engine.status_message or "cached" in failing_engine.status_message
        )
        # Conversion still works using cached rates
        ok, res, rate, _ = failing_engine.convert(10.0, "USD", "INR")
        self.assertTrue(ok)
        self.assertEqual(res, 800.0)


if __name__ == "__main__":
    unittest.main()
