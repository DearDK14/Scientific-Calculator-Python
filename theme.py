"""
theme.py
========
Visual styling, modern color schemes, typography, and theme management
for the CustomTkinter Scientific Calculator.
"""

import os
import json
import tkinter as tk
from typing import Tuple, Optional
import customtkinter as ctk


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

    # 9. Memory Bar Buttons (MC, MR, M+, M-, MS)
    BTN_MEMORY = {
        "fg_color": ("#1E293B", "#E2E8F0"),
        "hover_color": ("#334155", "#CBD5E1"),
        "text_color": ("#38BDF8", "#0284C7"),
        "corner_radius": 8,
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
    def button_memory(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="bold")

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
    """
    Manages application appearance mode (Dark / Light), persistence in calculator_settings.json,
    and automatic theme switching.
    """

    def __init__(self, settings_file: Optional[str] = None, initial_mode: str = "dark"):
        if settings_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.settings_file = os.path.join(base_dir, "calculator_settings.json")
        else:
            self.settings_file = settings_file

        self.current_mode = self._load_persisted_mode(default_mode=initial_mode)
        ctk.set_appearance_mode(self.current_mode)
        ctk.set_default_color_theme("blue")

    def _load_persisted_mode(self, default_mode: str = "dark") -> str:
        """Loads saved theme mode from settings JSON file if present."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    mode = data.get("theme", default_mode)
                    if mode in ("dark", "light"):
                        return mode
        except Exception:
            pass
        return default_mode

    def _save_persisted_mode(self) -> None:
        """Saves current appearance mode to settings JSON file."""
        try:
            data = {}
            if os.path.exists(self.settings_file):
                try:
                    with open(self.settings_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            data["theme"] = self.current_mode
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def toggle(self) -> str:
        """Toggles between 'dark' and 'light' modes, saves the choice, and returns the new mode."""
        self.current_mode = "light" if self.current_mode == "dark" else "dark"
        ctk.set_appearance_mode(self.current_mode)
        self._save_persisted_mode()
        return self.current_mode

    def set_mode(self, mode: str) -> None:
        """Sets appearance mode to 'dark' or 'light' and persists the choice."""
        if mode in ("dark", "light"):
            self.current_mode = mode
            ctk.set_appearance_mode(mode)
            self._save_persisted_mode()


class CTkToolTip:
    """
    Lightweight, modern hover tooltip for CustomTkinter widgets.
    Displays informative floating description on hover without external libraries.
    """

    def __init__(self, widget: ctk.CTkBaseClass, text: str, delay_ms: int = 400):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.tip_window: Optional[tk.Toplevel] = None
        self._after_id: Optional[str] = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event=None) -> None:
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, event=None) -> None:
        self._cancel()
        self._hide()

    def _cancel(self) -> None:
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self) -> None:
        if self.tip_window or not self.widget.winfo_exists():
            return
        try:
            x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
            y = self.widget.winfo_rooty() - 30
            if y < 10:
                y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        except Exception:
            return

        mode = ctk.get_appearance_mode().lower()
        bg = "#0F172A" if mode == "dark" else "#FFFFFF"
        fg = "#F8FAFC" if mode == "dark" else "#0F172A"
        border = "#38BDF8" if mode == "dark" else "#0284C7"

        try:
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes("-topmost", True)

            border_frame = tk.Frame(tw, background=border, padx=1, pady=1)
            border_frame.pack()
            inner_frame = tk.Frame(border_frame, background=bg, padx=8, pady=3)
            inner_frame.pack()
            lbl = tk.Label(
                inner_frame,
                text=self.text,
                justify=tk.LEFT,
                background=bg,
                foreground=fg,
                font=("Segoe UI", 9, "normal"),
            )
            lbl.pack()
        except Exception:
            self.tip_window = None

    def _hide(self) -> None:
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None
