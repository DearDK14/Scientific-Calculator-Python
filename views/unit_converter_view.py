"""
views/unit_converter_view.py
============================
Universal Unit Converter View for 12 Physical & Digital Measurement Domains:
Volume, Length, Weight and Mass, Temperature, Energy, Area,
Speed, Time, Power, Data, Pressure, and Angle.

Features:
- Live automatic conversion as user types or changes units
- From and To unit selection dropdowns
- Swap units button (⇄)
- Copy result button (📋) with visual feedback
- Clear input button (✕)
- Input validation and friendly error handling (e.g. absolute zero in Temperature)
- Unit formula reference readout (e.g. '1 m = 3.28084 ft')
- On-screen numeric keypad and full physical keyboard routing
- SI vs IEC unit system filter for Data converter
"""

from typing import Any, Dict, List, Optional
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip
from unit_converter_engine import UnitConverterEngine


class UnitConverterView(BaseModeView):
    """
    Modular, parameterized converter view for all physical and data unit types.
    """

    # Category titles mapping
    CATEGORY_TITLES = {
        "volume": "Volume Converter",
        "length": "Length Converter",
        "weight": "Weight and Mass Converter",
        "temperature": "Temperature Converter",
        "energy": "Energy Converter",
        "area": "Area Converter",
        "speed": "Speed Converter",
        "time": "Time Converter",
        "power": "Power Converter",
        "data": "Data Converter",
        "pressure": "Pressure Converter",
        "angle": "Angle Converter",
    }

    def __init__(self, parent: ctk.CTkFrame, app: Any, category: str = "volume", **kwargs):
        super().__init__(parent, app, **kwargs)
        self.category = category.lower().strip()
        self._copied_timer = None
        self.data_system = "all"  # 'all', 'si', 'iec'

        # Default units
        def_from, def_to = UnitConverterEngine.get_defaults(self.category)
        self.from_unit_var = ctk.StringVar(value=def_from)
        self.to_unit_var = ctk.StringVar(value=def_to)

        self._build_ui()
        self._convert()

    # -------------------------------------------------------------------------
    # BaseModeView Contract
    # -------------------------------------------------------------------------
    def get_title(self) -> str:
        return self.CATEGORY_TITLES.get(self.category, f"{self.category.capitalize()} Converter")

    def get_mode_id(self) -> str:
        return self.category

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

        # Optional Data System Filter (SI vs IEC)
        if self.category == "data":
            filter_row = ctk.CTkFrame(card, fg_color="transparent")
            filter_row.pack(fill="x", padx=14, pady=(10, 4))

            ctk.CTkLabel(
                filter_row,
                text="Unit Standard:",
                font=Fonts.label_badge(),
                text_color=Theme.TEXT_SECONDARY,
            ).pack(side="left", padx=(0, 8))

            self.data_seg = ctk.CTkSegmentedButton(
                filter_row,
                values=["All Units", "Decimal (SI)", "Binary (IEC)"],
                command=self._on_data_system_changed,
                font=Fonts.label_badge(),
                selected_color=Theme.ACCENT_PRIMARY,
                selected_hover_color=Theme.ACCENT_HOVER,
                height=28,
            )
            self.data_seg.set("All Units")
            self.data_seg.pack(side="left")

        # 1. "From" Section (Input Amount & Dropdown)
        from_frame = ctk.CTkFrame(card, fg_color="transparent")
        from_frame.pack(fill="x", padx=14, pady=(10, 4))
        from_frame.grid_columnconfigure(0, weight=1)
        from_frame.grid_columnconfigure(1, weight=0)

        self.input_entry = ctk.CTkEntry(
            from_frame,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            height=46,
            justify="right",
        )
        self.input_entry.insert(0, "1")
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<KeyRelease>", lambda e: self._convert())

        units = UnitConverterEngine.get_unit_list(self.category, self.data_system)
        self.from_dropdown = ctk.CTkOptionMenu(
            from_frame,
            values=units,
            variable=self.from_unit_var,
            command=lambda v: self._convert(),
            width=170,
            height=44,
            font=Fonts.button_bottom(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
        )
        self.from_dropdown.grid(row=0, column=1)

        # 2. Middle Action Bar (Swap ⇄, Clear ✕, Copy 📋)
        mid_bar = ctk.CTkFrame(card, fg_color="transparent")
        mid_bar.pack(fill="x", padx=14, pady=4)

        self.swap_btn = ctk.CTkButton(
            mid_bar,
            text="⇄ Swap",
            width=80,
            height=30,
            command=self._swap_units,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.swap_btn.pack(side="left", padx=(0, 6))
        CTkToolTip(self.swap_btn, "Swap From and To units")

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

        # 3. "To" Section (Result Readout & Dropdown)
        to_frame = ctk.CTkFrame(card, fg_color="transparent")
        to_frame.pack(fill="x", padx=14, pady=(4, 10))
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
            values=units,
            variable=self.to_unit_var,
            command=lambda v: self._convert(),
            width=170,
            height=44,
            font=Fonts.button_bottom(),
            fg_color=Theme.BTN_TOOL["fg_color"],
            button_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.BTN_TOOL["text_color"],
        )
        self.to_dropdown.grid(row=0, column=1)

        # 4. Formula & Error Status Bar
        status_bar = ctk.CTkFrame(card, fg_color="transparent")
        status_bar.pack(fill="x", padx=16, pady=(0, 10))

        self.formula_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.formula_label.pack(side="left")

        self.error_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ERROR,
            anchor="e",
        )
        self.error_label.pack(side="right")

    # -------------------------------------------------------------------------
    # On-Screen Compact Keypad
    # -------------------------------------------------------------------------
    def _build_keypad(self, parent: ctk.CTkFrame) -> None:
        keypad = ctk.CTkFrame(parent, fg_color="transparent")
        keypad.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))

        for c in range(4):
            keypad.grid_columnconfigure(c, weight=1)
        for r in range(4):
            keypad.grid_rowconfigure(r, weight=1)

        # Keypad Grid:
        # [7] [8] [9] [DEL]
        # [4] [5] [6] [C]
        # [1] [2] [3] [±]
        # [0] [.] [⇄] [📋]
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
            ("±", 2, 3, self._toggle_sign, Theme.BTN_NUMBER),

            ("0", 3, 0, lambda: self._append_input("0"), Theme.BTN_NUMBER),
            (".", 3, 1, lambda: self._append_input("."), Theme.BTN_NUMBER),
            ("⇄", 3, 2, self._swap_units, Theme.BTN_OPERATOR),
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
    # Conversion Logic & Actions
    # -------------------------------------------------------------------------
    def _convert(self) -> None:
        raw_text = self.input_entry.get().strip()
        if not raw_text:
            self.result_label.configure(text="0")
            self.formula_label.configure(text="")
            self.error_label.configure(text="")
            return

        try:
            val = float(raw_text)
        except ValueError:
            self.result_label.configure(text="--")
            self.error_label.configure(text="Invalid numeric input")
            return

        from_u = self.from_unit_var.get()
        to_u = self.to_unit_var.get()

        ok, result, err = UnitConverterEngine.convert(self.category, val, from_u, to_u)
        if not ok or result is None:
            self.result_label.configure(text="--")
            self.error_label.configure(text=err or "Conversion error")
            return

        self.error_label.configure(text="")
        formatted = UnitConverterEngine.format_value(result)
        self.result_label.configure(text=formatted)

        # Update formula reference
        formula = UnitConverterEngine.get_rate_formula(self.category, from_u, to_u)
        self.formula_label.configure(text=formula)

    def _swap_units(self) -> None:
        curr_from = self.from_unit_var.get()
        curr_to = self.to_unit_var.get()
        self.from_unit_var.set(curr_to)
        self.to_unit_var.set(curr_from)
        self._convert()

    def _clear_input(self) -> None:
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, "0")
        self._convert()

    def _append_input(self, char: str) -> None:
        curr = self.input_entry.get().strip()
        if curr == "0" and char != ".":
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, char)
        elif char == "." and "." in curr:
            return  # Prevent duplicate decimal point
        else:
            self.input_entry.insert("end", char)
        self._convert()

    def _backspace_input(self) -> None:
        curr = self.input_entry.get()
        if len(curr) <= 1:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, "0")
        else:
            self.input_entry.delete(len(curr) - 1, "end")
        self._convert()

    def _toggle_sign(self) -> None:
        curr = self.input_entry.get().strip()
        if not curr or curr == "0":
            return
        if curr.startswith("-"):
            self.input_entry.delete(0, 1)
        else:
            self.input_entry.insert(0, "-")
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

    def _on_data_system_changed(self, choice: str) -> None:
        if "Decimal" in choice:
            self.data_system = "si"
        elif "Binary" in choice:
            self.data_system = "iec"
        else:
            self.data_system = "all"

        new_units = UnitConverterEngine.get_unit_list(self.category, self.data_system)
        self.from_dropdown.configure(values=new_units)
        self.to_dropdown.configure(values=new_units)

        if self.from_unit_var.get() not in new_units:
            self.from_unit_var.set(new_units[0])
        if self.to_unit_var.get() not in new_units:
            self.to_unit_var.set(new_units[-1])

        self._convert()
