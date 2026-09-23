"""
currency_provider.py
====================
Configurable Exchange Rate Provider Interface and Engine for Currency Conversion.

Architecture:
- ExchangeRateProvider (Abstract Base Class)
- MockExchangeRateProvider (Deterministic mock provider for offline tests)
- ApiExchangeRateProvider (Live HTTPS provider using free public endpoints)
- Local persistent rate caching with timestamps
- Explicit labeling of live vs. cached/stale/offline rates
- Never claims live accuracy without a successful rate update
- Zero API keys in source code
"""

from abc import ABC, abstractmethod
import json
import os
import time
from typing import Dict, List, Optional, Tuple
import urllib.request
import urllib.error


# Common currency metadata: (Code, Name, Symbol)
SUPPORTED_CURRENCIES: List[Tuple[str, str, str]] = [
    ("USD", "US Dollar", "$"),
    ("EUR", "Euro", "€"),
    ("INR", "Indian Rupee", "₹"),
    ("GBP", "British Pound", "£"),
    ("JPY", "Japanese Yen", "¥"),
    ("AUD", "Australian Dollar", "A$"),
    ("CAD", "Canadian Dollar", "C$"),
    ("CHF", "Swiss Franc", "CHF"),
    ("CNY", "Chinese Yuan", "¥"),
    ("SGD", "Singapore Dollar", "S$"),
    ("NZD", "New Zealand Dollar", "NZ$"),
    ("AED", "UAE Dirham", "د.إ"),
]

# Baseline fallback rates relative to USD (used only when no network & no cache exists)
BASELINE_FALLBACK_RATES: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "INR": 83.50,
    "GBP": 0.79,
    "JPY": 155.0,
    "AUD": 1.52,
    "CAD": 1.36,
    "CHF": 0.90,
    "CNY": 7.24,
    "SGD": 1.35,
    "NZD": 1.64,
    "AED": 3.67,
}


class ExchangeRateProvider(ABC):
    """Abstract interface for exchange-rate providers."""

    @abstractmethod
    def fetch_rates(self, base_currency: str = "USD") -> Tuple[bool, Dict[str, float], Optional[str]]:
        """
        Fetches current exchange rates relative to base_currency.
        Returns: (success: bool, rates_dict: Dict[str, float], timestamp_or_error: str)
        """
        pass


class MockExchangeRateProvider(ExchangeRateProvider):
    """Deterministic mock provider for unit tests and offline testing."""

    def __init__(self, custom_rates: Optional[Dict[str, float]] = None):
        self.rates = custom_rates or {
            "USD": 1.0,
            "EUR": 0.85,
            "INR": 80.0,
            "GBP": 0.75,
            "JPY": 110.0,
            "AUD": 1.35,
            "CAD": 1.25,
            "CHF": 0.92,
            "CNY": 6.50,
            "SGD": 1.34,
            "NZD": 1.45,
            "AED": 3.67,
        }
        self.mock_timestamp = "2026-09-23 12:00:00 (Mock)"

    def fetch_rates(self, base_currency: str = "USD") -> Tuple[bool, Dict[str, float], Optional[str]]:
        base_rate = self.rates.get(base_currency, 1.0)
        # Normalize relative to base_currency
        normalized = {k: v / base_rate for k, v in self.rates.items()}
        return True, normalized, self.mock_timestamp


class ApiExchangeRateProvider(ExchangeRateProvider):
    """
    Live HTTPS exchange rate provider.
    Uses free public endpoint (https://open.er-api.com/v6/latest/{base}) with no key required.
    Times out safely to prevent UI hangs.
    """

    def __init__(self, endpoint_template: str = "https://open.er-api.com/v6/latest/{base}", timeout_sec: int = 5):
        self.endpoint_template = endpoint_template
        self.timeout_sec = timeout_sec

    def fetch_rates(self, base_currency: str = "USD") -> Tuple[bool, Dict[str, float], Optional[str]]:
        url = self.endpoint_template.format(base=base_currency)
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Antigravity-ModernCalculator/1.0"},
            )
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if data.get("result") == "success" and "rates" in data:
                rates = data["rates"]
                ts = data.get("time_last_update_utc", time.strftime("%Y-%m-%d %H:%M:%S UTC"))
                return True, rates, ts
            elif "rates" in data:
                return True, data["rates"], time.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                return False, {}, "API response did not contain expected rate data"

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception) as ex:
            return False, {}, f"Network connection unavailable: {ex}"


class CurrencyEngine:
    """
    Coordinates exchange-rate fetching, local disk caching, offline fallback,
    conversion calculations, and accuracy status tracking.
    """

    def __init__(
        self,
        provider: Optional[ExchangeRateProvider] = None,
        cache_file: Optional[str] = None,
    ):
        self.provider: ExchangeRateProvider = provider or ApiExchangeRateProvider()

        if cache_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.cache_file = os.path.join(base_dir, "currency_rates_cache.json")
        else:
            self.cache_file = cache_file

        # Active state
        self.rates: Dict[str, float] = dict(BASELINE_FALLBACK_RATES)
        self.last_update_time: str = "Baseline rates (offline)"
        self.is_live: bool = False
        self.status_message: str = "Initializing rates..."

        # Load cached rates from disk if available
        self._load_cache()

    def set_provider(self, provider: ExchangeRateProvider) -> None:
        """Configures a custom exchange-rate provider."""
        self.provider = provider

    def refresh_rates(self, force_network: bool = True) -> Tuple[bool, str]:
        """
        Attempts to fetch fresh exchange rates from provider.
        If network fails, falls back gracefully to cached or baseline rates
        and sets is_live=False to avoid false claims of live accuracy.
        """
        success, fetched_rates, info = self.provider.fetch_rates(base_currency="USD")

        if success and fetched_rates:
            self.rates = fetched_rates
            self.last_update_time = str(info)
            self.is_live = not isinstance(self.provider, MockExchangeRateProvider)
            self.status_message = f"🟢 Live rate updated: {self.last_update_time}"
            self._save_cache()
            return True, self.status_message
        else:
            # Fallback to cached rates
            self.is_live = False
            err_detail = info or "Connection failed"
            if self._load_cache():
                self.status_message = f"⚠️ Offline: using cached rates as of {self.last_update_time}"
            else:
                self.rates = dict(BASELINE_FALLBACK_RATES)
                self.last_update_time = "Built-in baseline"
                self.status_message = "⚠️ Offline: using baseline fallback rates"
            return False, f"{self.status_message} ({err_detail})"

    def convert(self, amount: float, from_curr: str, to_curr: str) -> Tuple[bool, Optional[float], Optional[float], Optional[str]]:
        """
        Converts amount from from_curr to to_curr using active rates.
        Returns: (success: bool, converted_amount: Optional[float], exchange_rate: Optional[float], error_message: Optional[str])
        """
        if amount < 0:
            return False, None, None, "Amount cannot be negative"

        if from_curr == to_curr:
            return True, float(amount), 1.0, None

        if from_curr not in self.rates:
            return False, None, None, f"Currency '{from_curr}' is not available in exchange rates"
        if to_curr not in self.rates:
            return False, None, None, f"Currency '{to_curr}' is not available in exchange rates"

        # Rates are relative to USD
        rate_from = self.rates[from_curr]
        rate_to = self.rates[to_curr]

        if rate_from <= 0:
            return False, None, None, f"Invalid rate for {from_curr}"

        # 1 From = (rate_to / rate_from) To
        exchange_rate = rate_to / rate_from
        result = amount * exchange_rate

        return True, result, exchange_rate, None

    def get_rate_formula(self, from_curr: str, to_curr: str) -> str:
        """Returns readable rate text, e.g. '1 USD = 83.50 INR'."""
        ok, _, rate, _ = self.convert(1.0, from_curr, to_curr)
        if not ok or rate is None:
            return ""
        if rate >= 1.0:
            rate_str = f"{rate:.4f}".rstrip("0").rstrip(".")
        else:
            rate_str = f"{rate:.6f}".rstrip("0").rstrip(".")
        return f"1 {from_curr} = {rate_str} {to_curr}"

    # -------------------------------------------------------------------------
    # Disk Caching
    # -------------------------------------------------------------------------
    def _save_cache(self) -> None:
        try:
            cache_payload = {
                "rates": self.rates,
                "timestamp": self.last_update_time,
                "saved_at": time.time(),
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f, indent=2)
        except Exception:
            pass

    def _load_cache(self) -> bool:
        if not os.path.exists(self.cache_file):
            return False
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "rates" in data and isinstance(data["rates"], dict):
                self.rates = data["rates"]
                self.last_update_time = data.get("timestamp", "Cached rates")
                return True
        except Exception:
            pass
        return False
