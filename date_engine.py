"""
date_engine.py
==============
Reusable Date Calculation Engine.

Provides:
- Date difference calculation (total days, weeks + days, exact calendar years + months + days)
- Date addition and subtraction (years, months, days) with leap year and month-end clipping
- Comprehensive date information (day of week, leap year detection, day of year, days remaining)
- Robust validation handling invalid months, days, and leap year bounds
"""

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional, Tuple


@dataclass
class DateDifferenceResult:
    """Detailed breakdown of the duration between two dates."""
    start_date: date
    end_date: date
    total_days: int
    weeks: int
    remaining_days_in_week: int
    years: int
    months: int
    days: int
    is_negative: bool  # True if end_date < start_date

    def summary_text(self) -> str:
        """Returns readable natural language description of difference."""
        if self.total_days == 0:
            return "Same day (0 days difference)"

        parts = []
        if self.years > 0:
            parts.append(f"{self.years} {'year' if self.years == 1 else 'years'}")
        if self.months > 0:
            parts.append(f"{self.months} {'month' if self.months == 1 else 'months'}")
        if self.days > 0:
            parts.append(f"{self.days} {'day' if self.days == 1 else 'days'}")

        detailed = ", ".join(parts) if parts else f"{self.total_days} days"
        prefix = "Earlier by " if self.is_negative else ""
        return f"{prefix}{detailed} ({self.total_days:,} total days)"


@dataclass
class DateAddResult:
    """Result of adding or subtracting a duration to/from a date."""
    original_date: date
    resulting_date: date
    operation: str  # 'add' or 'subtract'
    years_applied: int
    months_applied: int
    days_applied: int

    def formatted_result(self) -> str:
        """Returns standard full date string: 'Friday, November 20, 2026'."""
        return self.resulting_date.strftime("%A, %B %d, %Y")


@dataclass
class DateInfoResult:
    """Contextual calendar information for a specific date."""
    target_date: date
    day_of_week: str
    is_leap_year: bool
    day_of_year: int
    total_days_in_year: int
    days_remaining_in_year: int
    week_number: int
    quarter: int

    def leap_year_description(self) -> str:
        if self.is_leap_year:
            return f"Yes ({self.target_date.year} has 366 days)"
        return f"No ({self.target_date.year} has 365 days)"


class DateEngine:
    """
    Core static and instance methods for date calculations.
    Pure Python with zero external third-party dependencies.
    """

    # -------------------------------------------------------------------------
    # 1. Validation & Construction
    # -------------------------------------------------------------------------
    @staticmethod
    def validate_date_parts(year: int, month: int, day: int) -> Tuple[bool, Optional[date], Optional[str]]:
        """
        Validates year, month, and day.
        Returns (is_valid: bool, date_obj: Optional[date], error_message: Optional[str]).
        """
        if not (1 <= year <= 9999):
            return False, None, f"Year must be between 1 and 9999 (got {year})"

        if not (1 <= month <= 12):
            return False, None, f"Month must be between 1 and 12 (got {month})"

        _, max_days = calendar.monthrange(year, month)
        if not (1 <= day <= max_days):
            month_name = calendar.month_name[month]
            if month == 2 and not calendar.isleap(year) and day == 29:
                return False, None, f"{year} is not a leap year, so February has only 28 days"
            return False, None, f"{month_name} {year} has {max_days} days (got {day})"

        return True, date(year, month, day), None

    @staticmethod
    def parse_iso_date(date_str: str) -> Tuple[bool, Optional[date], Optional[str]]:
        """Parses YYYY-MM-DD string into a valid date."""
        try:
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
            return True, dt, None
        except ValueError as ex:
            return False, None, f"Invalid date format: {ex}"

    # -------------------------------------------------------------------------
    # 2. Date Difference Calculation
    # -------------------------------------------------------------------------
    @classmethod
    def calculate_date_difference(cls, start_date: date, end_date: date) -> DateDifferenceResult:
        """
        Computes total elapsed days, elapsed weeks, and exact calendar breakdown
        (years, months, days) between start_date and end_date.
        """
        is_negative = end_date < start_date
        d1, d2 = (end_date, start_date) if is_negative else (start_date, end_date)

        total_days = (d2 - d1).days
        weeks = total_days // 7
        remaining_days = total_days % 7

        # Exact calendar progression algorithm
        # y = d2.year - d1.year, m = d2.month - d1.month, d = d2.day - d1.day
        y = d2.year - d1.year
        m = d2.month - d1.month
        d = d2.day - d1.day

        if d < 0:
            # Borrow days from the previous month of d2
            prev_month = 12 if d2.month == 1 else d2.month - 1
            prev_year = d2.year - 1 if d2.month == 1 else d2.year
            _, days_in_prev_month = calendar.monthrange(prev_year, prev_month)
            d += days_in_prev_month
            m -= 1

        if m < 0:
            m += 12
            y -= 1

        return DateDifferenceResult(
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            weeks=weeks,
            remaining_days_in_week=remaining_days,
            years=y,
            months=m,
            days=d,
            is_negative=is_negative,
        )

    # -------------------------------------------------------------------------
    # 3. Add or Subtract Days & Months & Years
    # -------------------------------------------------------------------------
    @classmethod
    def add_subtract_date(
        cls,
        start_date: date,
        years: int = 0,
        months: int = 0,
        days: int = 0,
        operation: str = "add",
    ) -> Tuple[bool, Optional[DateAddResult], Optional[str]]:
        """
        Adds or subtracts a duration (years, months, days) to/from start_date.
        Correctly clips day-of-month at month-end boundaries (e.g. Jan 31 + 1 month -> Feb 28/29).
        Returns (success: bool, result: Optional[DateAddResult], error_message: Optional[str]).
        """
        op = operation.lower().strip()
        if op not in ("add", "subtract", "+", "-"):
            return False, None, f"Unsupported operation: {operation}"

        sign = 1 if op in ("add", "+") else -1

        # 1. Apply Year and Month shift
        total_months = (start_date.year * 12 + (start_date.month - 1)) + sign * (years * 12 + months)
        target_year = total_months // 12
        target_month = (total_months % 12) + 1

        if not (1 <= target_year <= 9999):
            return False, None, f"Resulting year {target_year} exceeds calendar range [1, 9999]"

        # Clip day to month range (e.g. Feb 30 -> Feb 28 or 29)
        _, max_days = calendar.monthrange(target_year, target_month)
        clipped_day = min(start_date.day, max_days)
        base_target_date = date(target_year, target_month, clipped_day)

        # 2. Apply Days shift via timedelta
        try:
            final_date = base_target_date + timedelta(days=sign * days)
            if not (1 <= final_date.year <= 9999):
                return False, None, f"Resulting date {final_date} exceeds calendar range [1, 9999]"
        except OverflowError:
            return False, None, "Date calculation overflowed allowable calendar range"

        result = DateAddResult(
            original_date=start_date,
            resulting_date=final_date,
            operation="add" if sign == 1 else "subtract",
            years_applied=years,
            months_applied=months,
            days_applied=days,
        )
        return True, result, None

    # -------------------------------------------------------------------------
    # 4. Date Information
    # -------------------------------------------------------------------------
    @classmethod
    def get_date_info(cls, target_date: date) -> DateInfoResult:
        """
        Extracts contextual calendar metrics for target_date:
        - Day of the week
        - Leap year detection
        - Day of the year
        - Total days in year and days remaining
        - ISO week number
        - Quarter of the year
        """
        is_leap = calendar.isleap(target_date.year)
        total_days_in_year = 366 if is_leap else 365
        day_of_year = target_date.timetuple().tm_yday
        days_remaining = total_days_in_year - day_of_year
        iso_week = target_date.isocalendar()[1]
        quarter = (target_date.month - 1) // 3 + 1
        day_of_week = target_date.strftime("%A")

        return DateInfoResult(
            target_date=target_date,
            day_of_week=day_of_week,
            is_leap_year=is_leap,
            day_of_year=day_of_year,
            total_days_in_year=total_days_in_year,
            days_remaining_in_year=days_remaining,
            week_number=iso_week,
            quarter=quarter,
        )
