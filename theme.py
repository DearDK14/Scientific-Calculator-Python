"""
theme.py
========
Visual styling, modern color schemes, typography, and theme management
for the CustomTkinter Scientific Calculator.
"""

import customtkinter as ctk
from typing import Tuple


class Theme:
    """
    Defines modern, professional color palettes for dark and light appearance modes.
    Colors are provided as tuples: (dark_mode_color, light_mode_color).
    """

    # Window & container backgrounds (Deep modern obsidian/slate)
    WINDOW_BG: Tuple[str, str] = ("#0F172A", "#F1F5F9")
    DISPLAY_BG: Tuple[str, str] = ("#1E293B", "#FFFFFF")
    PANEL_BG: Tuple[str, str] = ("#1E293B", "#E2E8F0")
    CARD_BG: Tuple[str, str] = ("#182030", "#FFFFFF")
    CARD_HOVER: Tuple[str, str] = ("#26334D", "#EAEFF7")
    BORDER_COLOR: Tuple[str, str] = ("#334155", "#CBD5E1")
    DIVIDER_COLOR: Tuple[str, str] = ("#2D3748", "#CBD5E1")

    # Text colors
    TEXT_PRIMARY: Tuple[str, str] = ("#F8FAFC", "#0F172A")
    TEXT_SECONDARY: Tuple[str, str] = ("#94A3B8", "#64748B")
    TEXT_ACCENT: Tuple[str, str] = ("#38BDF8", "#0284C7")
    TEXT_SUCCESS: Tuple[str, str] = ("#10B981", "#059669")

    # 1. Number Buttons (0-9, .)
    BTN_NUMBER = {
        "fg_color": ("#334155", "#FFFFFF"),
        "hover_color": ("#475569", "#F1F5F9"),
        "text_color": ("#F8FAFC", "#0F172A"),
        "corner_radius": 12,
    }

    # 2. Arithmetic Operators (÷, ×, −, +)
    BTN_OPERATOR = {
        "fg_color": ("#2563EB", "#2563EB"),
        "hover_color": ("#1D4ED8", "#1D4ED8"),
        "text_color": ("#FFFFFF", "#FFFFFF"),
        "corner_radius": 12,
    }

    # 3. Scientific Functions (sin, cos, tan, log, ln, √, powers, constants, etc.)
    BTN_SCIENTIFIC = {
        "fg_color": ("#1E293B", "#E2E8F0"),
        "hover_color": ("#334155", "#CBD5E1"),
        "text_color": ("#38BDF8", "#0284C7"),
        "corner_radius": 12,
    }

    # 4. Equals Button (=)
    BTN_EQUALS = {
        "fg_color": ("#10B981", "#10B981"),
        "hover_color": ("#059669", "#059669"),
        "text_color": ("#FFFFFF", "#FFFFFF"),
        "corner_radius": 12,
    }

    # 5. Clear / Delete Buttons (C, DEL)
    BTN_ACTION = {
        "fg_color": ("#EF4444", "#EF4444"),
        "hover_color": ("#DC2626", "#DC2626"),
        "text_color": ("#FFFFFF", "#FFFFFF"),
        "corner_radius": 12,
    }

    # 6. Bracket Buttons ((, ))
    BTN_BRACKET = {
        "fg_color": ("#1E293B", "#E2E8F0"),
        "hover_color": ("#334155", "#CBD5E1"),
        "text_color": ("#F8FAFC", "#0F172A"),
        "corner_radius": 12,
    }

    # 7. Header Tool / Toggle Buttons
    BTN_TOOL = {
        "fg_color": ("#1E293B", "#E2E8F0"),
        "hover_color": ("#334155", "#CBD5E1"),
        "text_color": ("#94A3B8", "#475569"),
        "corner_radius": 8,
    }

    # 8. Copy Button (Display header)
    BTN_COPY = {
        "fg_color": "transparent",
        "hover_color": ("#334155", "#E2E8F0"),
        "text_color": ("#94A3B8", "#64748B"),
        "corner_radius": 6,
    }


class Fonts:
    """Standardized font configurations for consistent responsive typography."""

    FONT_FAMILY = "Segoe UI"

    @classmethod
    def display_result(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=34, weight="bold")

    @classmethod
    def display_formula(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=15, weight="normal")

    @classmethod
    def button_number(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=18, weight="bold")

    @classmethod
    def button_operator(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=20, weight="bold")

    @classmethod
    def button_scientific(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="bold")

    @classmethod
    def button_bottom(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=16, weight="bold")

    @classmethod
    def label_badge(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=11, weight="bold")

    @classmethod
    def history_title(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=15, weight="bold")

    @classmethod
    def history_expr(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="normal")

    @classmethod
    def history_result(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=14, weight="bold")

    @classmethod
    def history_time(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=10, weight="normal")


class ThemeManager:
    """Manages application appearance mode (Dark / Light) and theme switching."""

    def __init__(self, initial_mode: str = "dark"):
        self.current_mode = initial_mode
        ctk.set_appearance_mode(self.current_mode)
        ctk.set_default_color_theme("blue")

    def toggle(self) -> str:
        """Toggles between 'dark' and 'light' modes and returns the new mode."""
        self.current_mode = "light" if self.current_mode == "dark" else "dark"
        ctk.set_appearance_mode(self.current_mode)
        return self.current_mode

    def set_mode(self, mode: str) -> None:
        """Sets appearance mode to 'dark', 'light', or 'system'."""
        if mode in ("dark", "light", "system"):
            self.current_mode = mode
            ctk.set_appearance_mode(mode)
