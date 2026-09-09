"""
theme.py
========
Visual styling, modern color schemes, typography, and theme management
for the CustomTkinter Scientific Calculator.
"""

import customtkinter as ctk
from typing import Dict, Any, Tuple


class Theme:
    """
    Defines color palettes for dark and light appearance modes.
    Colors are provided as tuples: (dark_mode_color, light_mode_color).
    """

    # Window & container backgrounds
    WINDOW_BG: Tuple[str, str] = ("#18191E", "#F3F4F8")
    DISPLAY_BG: Tuple[str, str] = ("#20222A", "#FFFFFF")
    PANEL_BG: Tuple[str, str] = ("#1E2028", "#E9EBF2")
    BORDER_COLOR: Tuple[str, str] = ("#2D313D", "#DCE0EB")

    # Text colors
    TEXT_PRIMARY: Tuple[str, str] = ("#FFFFFF", "#1A1C23")
    TEXT_SECONDARY: Tuple[str, str] = ("#8E95A5", "#6B7280")
    TEXT_ACCENT: Tuple[str, str] = ("#4DA3FF", "#1A73E8")

    # Button: Numbers (0-9, .)
    BTN_NUMBER = {
        "fg_color": ("#2B2D37", "#FFFFFF"),
        "hover_color": ("#383B47", "#F0F2F6"),
        "text_color": ("#FFFFFF", "#1A1C23"),
        "corner_radius": 8,
    }

    # Button: Basic Arithmetic Operators (+, -, ×, ÷)
    BTN_OPERATOR = {
        "fg_color": ("#2E3A59", "#E8F0FE"),
        "hover_color": ("#3B4B73", "#D2E3FC"),
        "text_color": ("#7CB1FF", "#1967D2"),
        "corner_radius": 8,
    }

    # Button: Equals (=)
    BTN_EQUALS = {
        "fg_color": ("#1A73E8", "#1A73E8"),
        "hover_color": ("#1558B0", "#1558B0"),
        "text_color": ("#FFFFFF", "#FFFFFF"),
        "corner_radius": 8,
    }

    # Button: Scientific Functions (sin, cos, tan, log, etc.)
    BTN_SCIENTIFIC = {
        "fg_color": ("#232530", "#EEF1F7"),
        "hover_color": ("#2F3240", "#DFE4EE"),
        "text_color": ("#A5B4CB", "#3C4043"),
        "corner_radius": 8,
    }

    # Button: Clear / Action (AC, C, ⌫)
    BTN_ACTION = {
        "fg_color": ("#3D2529", "#FCE8E6"),
        "hover_color": ("#4E2E34", "#FAD2CF"),
        "text_color": ("#F28B82", "#C5221F"),
        "corner_radius": 8,
    }

    # Button: Memory (MC, MR, M+, M-, MS)
    BTN_MEMORY = {
        "fg_color": "transparent",
        "hover_color": ("#2B2D37", "#E4E7ED"),
        "text_color": ("#8E95A5", "#5F6368"),
        "corner_radius": 6,
    }

    # Button: Header / Tool icon buttons
    BTN_TOOL = {
        "fg_color": ("#262832", "#E8EAF0"),
        "hover_color": ("#333744", "#DADDE6"),
        "text_color": ("#A5B4CB", "#44474E"),
        "corner_radius": 8,
    }


class Fonts:
    """Standardized font configurations for consistent responsive typography."""

    FONT_FAMILY = "Segoe UI"

    @classmethod
    def display_result(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=32, weight="bold")

    @classmethod
    def display_formula(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="normal")

    @classmethod
    def button_main(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=16, weight="bold")

    @classmethod
    def button_scientific(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="normal")

    @classmethod
    def button_memory(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=11, weight="bold")

    @classmethod
    def label_badge(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=10, weight="bold")

    @classmethod
    def history_title(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=14, weight="bold")

    @classmethod
    def history_item(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="normal")


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
