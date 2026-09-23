"""
views/currency_view.py
======================
Currency Converter Mode View.

Features:
- Live conversion across major world currencies: USD, EUR, INR, GBP, JPY, AUD, CAD, CHF, CNY, etc.
- Configurable exchange-rate provider interface with disk caching and offline support
- Rate refresh button (🔄) with non-blocking background fetching
- Live vs. offline/cached accuracy status banner
- Currency swap button (⇄), clear (✕), and copy (📋) buttons
- Compact on-screen keypad and full keyboard routing
"""

import threading
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip
from currency_provider import CurrencyEngine, SUPPORTED_CURRENCIES


class CurrencyView(BaseModeView):
    """
    Modular Currency Converter mode view.
    """

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, app, **kwargs)
        self.engine = CurrencyEngine()
        self._copied_timer = None
        self._is_refreshing = False

        # Build currency display options, e.g. "USD - US Dollar ($)"
        self.currency_codes = [c[0] for c in SUPPORTED_CURRENCIES]
        self.display_to_code: Dict[str, str] = {}
        self.code_to_display: Dict[str, str] = {}
        self.currency_options: List[str] = []

        for code, name, symbol in SUPPORTED_CURRENCIES:
            label = f"{code} - {name} ({symbol})"
            self.display_to_code[label] = code
            self.code_to_display[code] = label
            self.currency_options.append(label)

        self.from_var = ctk.StringVar(value=self.code_to_display.get("USD", "USD"))
        self.to_var = ctk.StringVar(value=self.code_to_display.get("INR", "INR"))

        self._build_ui()
        self._convert()

    # -------------------------------------------------------------------------
    # BaseModeView Contract
    # -------------------------------------------------------------------------
    def get_title(self) -> str:
        return "Currency Converter"

    def get_mode_id(self) -> str:
        return "currency"

    def handles_keyboard(self) -> bool:
        return True

    def on_activate(self) -> None:
        self._convert()

    def handle_key_action(self, action_type: str, value: Optional[str] = None) -> None:
        if action_type == "number" and value:
            self._append_input(value)
        elif action_type == "decimal":
            self._append_input(".")
        elif action_type == "backspace":
            self._backspace_input()
        elif action_type in ("clear", "all_clear"):
            self._clear_input()
        elif action_type == "copy":
            self._copy_result()

    # -------------------------------------------------------------------------
    # UI Layout Construction
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top Conversion Card
        self.grid_rowconfigure(1, weight=1)  # On-screen Keypad

        self._build_conversion_card(self)
        self._build_keypad(self)

    def _build_conversion_card(self, parent: ctk.CTkFrame) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        card.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 8))
        card.grid_columnconfigure(0, weight=1)

        # 1. Status Banner (Live vs. Offline/Cached + Refresh Button)
        status_bar = ctk.CTkFrame(card, fg_color="transparent")
        status_bar.pack(fill="x", padx=14, pady=(10, 4))
        status_bar.grid_columnconfigure(0, weight=1)
        status_bar.grid_columnconfigure(1, weight=0)

        self.status_label = ctk.CTkLabel(
            status_bar,
            text=self.engine.status_message,
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            status_bar,
            text="🔄 Refresh",
            width=85,
            height=28,
            command=self._on_refresh_rates,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.refresh_btn.grid(row=0, column=1)
        CTkToolTip(self.refresh_btn, "Fetch latest exchange rates from provider")

        # 2. "From" Currency Row
        from_frame = ctk.CTkFrame(card, fg_color="transparent")
        from_frame.pack(fill="x", padx=14, pady=(4, 6))
        from_frame.grid_columnconfigure(0, weight=1)
        from_frame.grid_columnconfigure(1, weight=0)

        self.amount_entry = ctk.CTkEntry(
            from_frame,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            height=46,
            justify="right",
        )
        self.amount_entry.insert(0, "1")
        self.amount_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.amount_entry.bind("<KeyRelease>", lambda e: self._convert())

        self.from_dropdown = ctk.CTkOptionMenu(
            from_frame,
            values=self.currency_options,
            variable=self.from_var,
            command=lambda v: self._convert(),
            width=210,
            height=44,
            font=Fonts.label_badge(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
        )
        self.from_dropdown.grid(row=0, column=1)

        # 3. Middle Action Bar (Swap ⇄, Clear ✕, Copy 📋)
        mid_bar = ctk.CTkFrame(card, fg_color="transparent")
        mid_bar.pack(fill="x", padx=14, pady=2)

        self.swap_btn = ctk.CTkButton(
            mid_bar,
            text="⇄ Swap",
            width=80,
            height=30,
            command=self._swap_currencies,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.swap_btn.pack(side="left", padx=(0, 6))
        CTkToolTip(self.swap_btn, "Swap From and To currencies")

        self.clear_btn = ctk.CTkButton(
            mid_bar,
            text="✕ Clear",
            width=70,
            height=30,
            command=self._clear_input,
            font=Fonts.label_badge(),
            **Theme.BTN_ACTION,
        )
        self.clear_btn.pack(side="left", padx=(0, 6))

        self.copy_btn = ctk.CTkButton(
            mid_bar,
            text="📋 Copy",
            width=75,
            height=30,
            command=self._copy_result,
            font=Fonts.label_badge(),
            **Theme.BTN_COPY,
        )
        self.copy_btn.pack(side="left")
        CTkToolTip(self.copy_btn, "Copy converted result")

        # 4. "To" Currency Row
        to_frame = ctk.CTkFrame(card, fg_color="transparent")
        to_frame.pack(fill="x", padx=14, pady=(6, 8))
        to_frame.grid_columnconfigure(0, weight=1)
        to_frame.grid_columnconfigure(1, weight=0)

        # Read-only Result Box
        self.result_box = ctk.CTkFrame(
            to_frame,
            fg_color=Theme.DISPLAY_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=8,
            height=46,
        )
        self.result_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.result_box.pack_propagate(False)

        self.result_label = ctk.CTkLabel(
            self.result_box,
            text="--",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=Theme.TEXT_ACCENT,
            anchor="e",
        )
        self.result_label.pack(fill="both", expand=True, padx=12)

        self.to_dropdown = ctk.CTkOptionMenu(
            to_frame,
            values=self.currency_options,
            variable=self.to_var,
            command=lambda v: self._convert(),
            width=210,
            height=44,
            font=Fonts.label_badge(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
        )
        self.to_dropdown.grid(row=0, column=1)

        # 5. Formula & Error Status
        formula_row = ctk.CTkFrame(card, fg_color="transparent")
        formula_row.pack(fill="x", padx=16, pady=(0, 10))

        self.formula_label = ctk.CTkLabel(
            formula_row,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.formula_label.pack(side="left")

        self.error_label = ctk.CTkLabel(
            formula_row,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ERROR,
            anchor="e",
        )
        self.error_label.pack(side="right")

    # -------------------------------------------------------------------------
    # Keypad
    # -------------------------------------------------------------------------
    def _build_keypad(self, parent: ctk.CTkFrame) -> None:
        keypad = ctk.CTkFrame(parent, fg_color="transparent")
        keypad.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))

        for c in range(4):
            keypad.grid_columnconfigure(c, weight=1)
        for r in range(4):
            keypad.grid_rowconfigure(r, weight=1)

        key_defs = [
            ("7", 0, 0, lambda: self._append_input("7"), Theme.BTN_NUMBER),
            ("8", 0, 1, lambda: self._append_input("8"), Theme.BTN_NUMBER),
            ("9", 0, 2, lambda: self._append_input("9"), Theme.BTN_NUMBER),
            ("DEL", 0, 3, self._backspace_input, Theme.BTN_ACTION),

            ("4", 1, 0, lambda: self._append_input("4"), Theme.BTN_NUMBER),
            ("5", 1, 1, lambda: self._append_input("5"), Theme.BTN_NUMBER),
            ("6", 1, 2, lambda: self._append_input("6"), Theme.BTN_NUMBER),
            ("C", 1, 3, self._clear_input, Theme.BTN_ACTION),

            ("1", 2, 0, lambda: self._append_input("1"), Theme.BTN_NUMBER),
            ("2", 2, 1, lambda: self._append_input("2"), Theme.BTN_NUMBER),
            ("3", 2, 2, lambda: self._append_input("3"), Theme.BTN_NUMBER),
            ("00", 2, 3, lambda: self._append_input("00"), Theme.BTN_NUMBER),

            ("0", 3, 0, lambda: self._append_input("0"), Theme.BTN_NUMBER),
            (".", 3, 1, lambda: self._append_input("."), Theme.BTN_NUMBER),
            ("⇄", 3, 2, self._swap_currencies, Theme.BTN_OPERATOR),
            ("=", 3, 3, self._convert, Theme.BTN_EQUALS),
        ]

        for text, r, c, cmd, style in key_defs:
            btn = ctk.CTkButton(
                keypad,
                text=text,
                command=cmd,
                font=Fonts.button_standard(),
                **style,
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

    # -------------------------------------------------------------------------
    # Actions & Conversions
    # -------------------------------------------------------------------------
    def _convert(self) -> None:
        raw = self.amount_entry.get().strip()
        if not raw:
            self.result_label.configure(text="0.00")
            self.formula_label.configure(text="")
            self.error_label.configure(text="")
            return

        try:
            val = float(raw)
        except ValueError:
            self.result_label.configure(text="--")
            self.error_label.configure(text="Invalid numeric amount")
            return

        from_code = self.display_to_code.get(self.from_var.get(), "USD")
        to_code = self.display_to_code.get(self.to_var.get(), "INR")

        ok, converted, rate, err = self.engine.convert(val, from_code, to_code)
        if not ok or converted is None:
            self.result_label.configure(text="--")
            self.error_label.configure(text=err or "Conversion failed")
            return

        self.error_label.configure(text="")
        self.result_label.configure(text=f"{converted:,.2f}")
        formula = self.engine.get_rate_formula(from_code, to_code)
        self.formula_label.configure(text=formula)

    def _swap_currencies(self) -> None:
        curr_from = self.from_var.get()
        curr_to = self.to_var.get()
        self.from_var.set(curr_to)
        self.to_var.set(curr_from)
        self._convert()

    def _clear_input(self) -> None:
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, "0")
        self._convert()

    def _append_input(self, char: str) -> None:
        curr = self.amount_entry.get().strip()
        if curr == "0" and char != ".":
            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, char)
        elif char == "." and "." in curr:
            return
        else:
            self.amount_entry.insert("end", char)
        self._convert()

    def _backspace_input(self) -> None:
        curr = self.amount_entry.get()
        if len(curr) <= 1:
            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, "0")
        else:
            self.amount_entry.delete(len(curr) - 1, "end")
        self._convert()

    def _copy_result(self) -> None:
        res = self.result_label.cget("text")
        if res and res != "--":
            self.app.clipboard_clear()
            self.app.clipboard_append(res)
            self._show_copy_feedback("Copied!")

    def _show_copy_feedback(self, msg: str) -> None:
        orig = self.copy_btn.cget("text")
        self.copy_btn.configure(text=msg, text_color=Theme.TEXT_ACCENT)

        if self._copied_timer:
            self.after_cancel(self._copied_timer)

        def restore():
            self.copy_btn.configure(text=orig, text_color=Theme.BTN_COPY["text_color"])

        self._copied_timer = self.after(1400, restore)

    def _on_refresh_rates(self) -> None:
        if self._is_refreshing:
            return
        self._is_refreshing = True
        self.refresh_btn.configure(text="⏳ Fetching...", state="disabled")
        self.status_label.configure(text="Fetching latest rates from provider...")

        def worker():
            success, msg = self.engine.refresh_rates()

            def update_ui():
                self._is_refreshing = False
                self.refresh_btn.configure(text="🔄 Refresh", state="normal")
                self.status_label.configure(text=self.engine.status_message)
                self._convert()

            self.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()
