"""
scientific_view.py
==================
Complete Scientific Calculator view.
Integrates pure scientific math engine, display card, memory toolbar,
scientific function keypad, and standard arithmetic controls.
"""

import os
import re
import tkinter as tk
from typing import Any, Optional
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip
from calculator import CalculatorEngine


class ScientificView(BaseModeView):
    """
    Modular Scientific Calculator mode view.
    Hosts display, memory bar, scientific functions, and arithmetic keypad.
    """

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, app, **kwargs)
        self.engine: CalculatorEngine = self.app.engine

        self._copied_timer = None
        self._paste_timer = None

        self._build_ui()

    def get_title(self) -> str:
        return "Scientific"

    def get_mode_id(self) -> str:
        return "scientific"

    def handles_keyboard(self) -> bool:
        return True

    def on_activate(self) -> None:
        """Refreshes display and memory/history linkages on activation."""
        self._update_display()

    # -------------------------------------------------------------------------
    # UI Construction
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Display Card
        self.grid_rowconfigure(1, weight=0)  # Memory Bar
        self.grid_rowconfigure(2, weight=6)  # Scientific Keys (6 rows)
        self.grid_rowconfigure(3, weight=5)  # Main Keypad (4 rows)
        self.grid_rowconfigure(4, weight=1)  # Bottom Row (1 row)

        self._build_display(self)
        self._build_memory_bar(self)
        self._build_scientific_section(self)
        self._build_main_keypad(self)
        self._build_bottom_row(self)

    def _build_display(self, parent: ctk.CTkFrame) -> None:
        """Display Card with DEG/RAD badge, Memory (M) badge, and Copy action."""
        self.display_card = ctk.CTkFrame(
            parent,
            fg_color=Theme.DISPLAY_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=14,
        )
        self.display_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.display_card.grid_columnconfigure(0, weight=1)

        disp_header = ctk.CTkFrame(self.display_card, fg_color="transparent")
        disp_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
        disp_header.grid_columnconfigure(1, weight=1)

        # Left Badges (DEG/RAD + Memory M Indicator)
        left_badges = ctk.CTkFrame(disp_header, fg_color="transparent")
        left_badges.grid(row=0, column=0, sticky="w")

        self.badge_label = ctk.CTkLabel(
            left_badges,
            text=self.engine.angle_mode,
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ACCENT,
            anchor="w",
        )
        self.badge_label.pack(side="left")

        self.memory_badge = ctk.CTkLabel(
            left_badges,
            text="" if not self.engine.has_memory else "M",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ACCENT,
            anchor="w",
            width=18,
        )
        self.memory_badge.pack(side="left", padx=(8, 0))

        # Copy Action Container
        copy_box = ctk.CTkFrame(disp_header, fg_color="transparent")
        copy_box.grid(row=0, column=2, sticky="e")

        self.feedback_label = ctk.CTkLabel(
            copy_box,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SUCCESS,
            anchor="e",
        )
        self.feedback_label.pack(side="left", padx=(0, 6))

        self.copy_btn = ctk.CTkButton(
            copy_box,
            text="📋 Copy",
            width=65,
            height=24,
            command=self._copy_to_clipboard,
            font=Fonts.label_badge(),
            **Theme.BTN_COPY,
        )
        self.copy_btn.pack(side="left")
        CTkToolTip(self.copy_btn, "Copy current result (Ctrl+C)")

        # Expression line
        self.expression_label = ctk.CTkLabel(
            self.display_card,
            text="",
            font=Fonts.display_formula(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="e",
        )
        self.expression_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 2))

        # Primary Result line
        self.result_label = ctk.CTkLabel(
            self.display_card,
            text="0",
            font=Fonts.display_result(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="e",
        )
        self.result_label.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 12))

    def _build_memory_bar(self, parent: ctk.CTkFrame) -> None:
        """5-button Memory Row: MC, MR, M+, M-, MS."""
        mem_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mem_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        for col in range(5):
            mem_frame.grid_columnconfigure(col, weight=1)

        mem_buttons = [
            ("MC", self._on_memory_clear, "Memory Clear: erase saved value"),
            ("MR", self._on_memory_recall, "Memory Recall: paste saved value"),
            ("M+", self._on_memory_add, "Memory Add: add current value to memory"),
            ("M-", self._on_memory_subtract, "Memory Subtract: subtract current value from memory"),
            ("MS", self._on_memory_store, "Memory Store: save current value in memory"),
        ]

        self.memory_buttons = {}
        for col, (label, cmd, tip) in enumerate(mem_buttons):
            btn = ctk.CTkButton(
                mem_frame,
                text=label,
                command=cmd,
                font=Fonts.button_memory(),
                height=28,
                **Theme.BTN_MEMORY,
            )
            btn.grid(row=0, column=col, padx=2, sticky="ew")
            CTkToolTip(btn, tip)
            self.memory_buttons[label] = btn

    def _build_scientific_section(self, parent: ctk.CTkFrame) -> None:
        """Scientific Section (3 columns x 6 rows)"""
        self.sci_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.sci_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 8))

        for c in range(3):
            self.sci_frame.grid_columnconfigure(c, weight=1)

        sci_buttons = [
            [("sin", lambda: self._on_func("sin"), "Sine: sin(x) in DEG or RAD"),
             ("cos", lambda: self._on_func("cos"), "Cosine: cos(x) in DEG or RAD"),
             ("tan", lambda: self._on_func("tan"), "Tangent: tan(x) in DEG or RAD")],
            [("asin", lambda: self._on_func("asin"), "Inverse Sine: arcsin(x), -1 ≤ x ≤ 1"),
             ("acos", lambda: self._on_func("acos"), "Inverse Cosine: arccos(x), -1 ≤ x ≤ 1"),
             ("atan", lambda: self._on_func("atan"), "Inverse Tangent: arctan(x)")],
            [("log", lambda: self._on_func("log10"), "Common Logarithm: log10(x), x > 0"),
             ("ln", lambda: self._on_func("ln"), "Natural Logarithm: ln(x), x > 0"),
             ("√", self._on_sqrt, "Square Root: √(x), x ≥ 0")],
            [("x²", lambda: self._on_unary("sqr"), "Square: x² (raise to power 2)"),
             ("xʸ", lambda: self._on_operator("^"), "Power: x^y (x raised to y)"),
             ("π", lambda: self._on_constant("pi"), "Pi constant (≈ 3.14159)")],
            [("e", lambda: self._on_constant("e"), "Euler's constant (≈ 2.71828)"),
             ("!", lambda: self._on_unary("fact"), "Factorial: x! (non-negative integer)"),
             ("%", lambda: self._on_unary("percent"), "Percentage: x / 100")],
            [("exp", self._on_exp, "Exponential: e^x"),
             ("1/x", lambda: self._on_unary("recip"), "Reciprocal: 1 / x"),
             ("|x|", lambda: self._on_unary("abs"), "Absolute Value: |x|")],
        ]

        for r, row in enumerate(sci_buttons):
            self.sci_frame.grid_rowconfigure(r, weight=1)
            for c, (label, cmd, tip) in enumerate(row):
                btn = ctk.CTkButton(
                    self.sci_frame,
                    text=label,
                    command=cmd,
                    font=Fonts.button_scientific(),
                    **Theme.BTN_SCIENTIFIC,
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                CTkToolTip(btn, tip)

    def _build_main_keypad(self, parent: ctk.CTkFrame) -> None:
        """Main Numeric & Arithmetic Keypad (4 columns x 4 rows)"""
        self.main_keypad = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_keypad.grid(row=3, column=0, sticky="nsew", pady=(0, 8))

        for c in range(4):
            self.main_keypad.grid_columnconfigure(c, weight=1)

        main_buttons = [
            [("7", lambda: self._on_number("7"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("8", lambda: self._on_number("8"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("9", lambda: self._on_number("9"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("÷", lambda: self._on_operator("/"), Theme.BTN_OPERATOR, Fonts.button_operator())],
            [("4", lambda: self._on_number("4"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("5", lambda: self._on_number("5"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("6", lambda: self._on_number("6"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("×", lambda: self._on_operator("*"), Theme.BTN_OPERATOR, Fonts.button_operator())],
            [("1", lambda: self._on_number("1"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("2", lambda: self._on_number("2"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("3", lambda: self._on_number("3"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("−", lambda: self._on_operator("-"), Theme.BTN_OPERATOR, Fonts.button_operator())],
            [("0", lambda: self._on_number("0"), Theme.BTN_NUMBER, Fonts.button_number()),
             (".", self._on_decimal, Theme.BTN_NUMBER, Fonts.button_number()),
             ("±", self._on_toggle_sign, Theme.BTN_NUMBER, Fonts.button_number()),
             ("+", lambda: self._on_operator("+"), Theme.BTN_OPERATOR, Fonts.button_operator())],
        ]

        for r, row in enumerate(main_buttons):
            self.main_keypad.grid_rowconfigure(r, weight=1)
            for c, (label, cmd, styling, font) in enumerate(row):
                btn = ctk.CTkButton(
                    self.main_keypad,
                    text=label,
                    command=cmd,
                    font=font,
                    **styling,
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                if label == "±":
                    CTkToolTip(btn, "Toggle Sign: positive / negative (±)")

    def _build_bottom_row(self, parent: ctk.CTkFrame) -> None:
        """Bottom Actions Row (5 columns x 1 row): C DEL ( ) ="""
        self.bottom_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.bottom_frame.grid(row=4, column=0, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)

        for c in range(5):
            self.bottom_frame.grid_columnconfigure(c, weight=1)

        bottom_buttons = [
            ("C", self._on_clear, Theme.BTN_ACTION, Fonts.button_bottom(), "Clear input (Escape)"),
            ("DEL", self._on_backspace, Theme.BTN_ACTION, Fonts.button_bottom(), "Backspace: delete last character"),
            ("(", lambda: self._on_bracket("("), Theme.BTN_BRACKET, Fonts.button_bottom(), "Open parenthesis: ("),
            (")", lambda: self._on_bracket(")"), Theme.BTN_BRACKET, Fonts.button_bottom(), "Close parenthesis: )"),
            ("=", self._on_equals, Theme.BTN_EQUALS, Fonts.button_operator(), "Calculate result (Enter)"),
        ]

        for c, (label, cmd, styling, font, tip) in enumerate(bottom_buttons):
            btn = ctk.CTkButton(
                self.bottom_frame,
                text=label,
                command=cmd,
                font=font,
                **styling,
            )
            btn.grid(row=0, column=c, padx=3, pady=3, sticky="nsew")
            CTkToolTip(btn, tip)

    # -------------------------------------------------------------------------
    # Display Updates
    # -------------------------------------------------------------------------
    def _update_display(self) -> None:
        self.expression_label.configure(text=self.engine.previous_expression)

        text = self.engine.current_input
        if len(text) > 18:
            size = 20
        elif len(text) > 13:
            size = 26
        else:
            size = 34

        self.result_label.configure(
            text=text,
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=size, weight="bold"),
        )
        self.badge_label.configure(text=self.engine.angle_mode)

        # Update Memory Indicator Badge
        self.memory_badge.configure(text="M" if self.engine.has_memory else "")

        # Update Memory Button states
        if hasattr(self, "memory_buttons"):
            has_mem = self.engine.has_memory
            mc_mr_state = "normal" if has_mem else "disabled"
            mc_mr_color = Theme.BTN_MEMORY["text_color"] if has_mem else ("#475569", "#94A3B8")
            self.memory_buttons["MC"].configure(state=mc_mr_state, text_color=mc_mr_color)
            self.memory_buttons["MR"].configure(state=mc_mr_state, text_color=mc_mr_color)

        # Notify app shell to refresh right-side history/memory panel if open
        if hasattr(self.app, "history_memory_panel"):
            self.app.history_memory_panel.refresh()

    def toggle_angle_mode(self) -> str:
        """Toggles between DEG and RAD."""
        new_mode = self.engine.toggle_angle_mode()
        self._update_display()
        return new_mode

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------
    def _on_number(self, num: str) -> None:
        self.engine.append_number(num)
        self._update_display()

    def _on_decimal(self) -> None:
        self.engine.append_decimal()
        self._update_display()

    def _on_operator(self, op: str) -> None:
        self.engine.append_operator(op)
        self._update_display()

    def _on_bracket(self, bracket: str) -> None:
        self.engine.append_bracket(bracket)
        self._update_display()

    def _on_constant(self, const: str) -> None:
        self.engine.append_constant(const)
        self._update_display()

    def _on_func(self, func: str) -> None:
        self.engine.apply_function(func)
        self._update_display()

    def _on_unary(self, op: str) -> None:
        self.engine.apply_unary_operation(op)
        self._update_display()

    def _on_sqrt(self) -> None:
        val_str = self.engine.current_input.strip()
        try:
            float(val_str)
            self.engine.apply_unary_operation("sqrt")
            self._update_display()
        except ValueError:
            self._on_func("sqrt")

    def _on_exp(self) -> None:
        val_str = self.engine.current_input.strip()
        try:
            float(val_str)
            self.engine.apply_unary_operation("exp")
            self._update_display()
        except ValueError:
            self._on_func("exp")

    def _on_toggle_sign(self) -> None:
        self.engine.toggle_sign()
        self._update_display()

    def _on_equals(self) -> None:
        self.engine.calculate()
        self._update_display()

    def _on_backspace(self) -> None:
        self.engine.backspace()
        self._update_display()

    def _on_clear(self) -> None:
        self.engine.clear()
        self._update_display()

    def _on_all_clear(self) -> None:
        self.engine.all_clear()
        self._update_display()

    # Memory Handlers
    def _on_memory_clear(self) -> None:
        self.engine.memory_clear()
        self._update_display()
        self._show_feedback("Memory Cleared", Theme.TEXT_SECONDARY)

    def _on_memory_recall(self) -> None:
        self.engine.memory_recall()
        self._update_display()
        self._show_feedback("Memory Recalled", Theme.TEXT_ACCENT)

    def _on_memory_store(self) -> None:
        if self.engine.memory_store():
            self._update_display()
            self._show_feedback("Stored to M", Theme.TEXT_SUCCESS)
        else:
            self._show_feedback("Error", Theme.BTN_ACTION["fg_color"])

    def _on_memory_add(self) -> None:
        if self.engine.memory_add():
            self._update_display()
            self._show_feedback("Added to M", Theme.TEXT_SUCCESS)
        else:
            self._show_feedback("Error", Theme.BTN_ACTION["fg_color"])

    def _on_memory_subtract(self) -> None:
        if self.engine.memory_subtract():
            self._update_display()
            self._show_feedback("Subtracted from M", Theme.TEXT_SUCCESS)
        else:
            self._show_feedback("Error", Theme.BTN_ACTION["fg_color"])

    # Clipboard & Feedback
    def _copy_to_clipboard(self, event=None) -> None:
        text_to_copy = self.engine.current_input.strip()
        if not text_to_copy or "Error" in text_to_copy:
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            self.update()
            self._show_copied_feedback()
        except Exception:
            pass

    def _paste_from_clipboard(self, event=None) -> None:
        try:
            raw_text = self.clipboard_get()
        except Exception:
            return

        cleaned = raw_text.strip().replace("\n", "").replace("\r", "")
        if not cleaned:
            return

        allowed_pattern = r"^[0-9+\-*/()×÷−.\^%! a-zA-Z]*$"
        if not re.match(allowed_pattern, cleaned):
            self._show_feedback("Invalid paste data", Theme.BTN_ACTION["fg_color"])
            return

        if self.engine.is_error or self.engine.is_new_calculation or self.engine.current_input == "0":
            self.engine.current_input = cleaned
            self.engine.is_new_calculation = False
            self.engine._is_error = False
        else:
            self.engine.current_input += f" {cleaned}"
            self.engine.is_new_calculation = False

        self._update_display()
        self._show_feedback("Pasted!", Theme.TEXT_SUCCESS)

    def _select_all(self, event=None) -> None:
        self.display_card.configure(border_color="#38BDF8", border_width=2)
        self.after(400, lambda: self.display_card.configure(
            border_color=Theme.BORDER_COLOR, border_width=1
        ))

    def _show_copied_feedback(self) -> None:
        self.copy_btn.configure(text="✓ Copied!", text_color=Theme.TEXT_SUCCESS[0])
        self._show_feedback("Result copied", Theme.TEXT_SUCCESS)
        if self._copied_timer:
            self.after_cancel(self._copied_timer)
        self._copied_timer = self.after(1500, self._reset_copy_btn)

    def _reset_copy_btn(self) -> None:
        self.copy_btn.configure(text="📋 Copy", text_color=Theme.BTN_COPY["text_color"])

    def _show_feedback(self, msg: str, color_tuple) -> None:
        color = color_tuple[0] if isinstance(color_tuple, tuple) else color_tuple
        self.feedback_label.configure(text=msg, text_color=color)
        if self._paste_timer:
            self.after_cancel(self._paste_timer)
        self._paste_timer = self.after(1600, lambda: self.feedback_label.configure(text=""))

    def handle_key_action(self, action_type: str, value: Optional[str] = None) -> None:
        """Processes global keyboard inputs routed from main shell."""
        if action_type == "number" and value is not None:
            self._on_number(value)
        elif action_type == "operator" and value is not None:
            self._on_operator(value)
        elif action_type == "decimal":
            self._on_decimal()
        elif action_type == "bracket" and value is not None:
            self._on_bracket(value)
        elif action_type == "constant" and value is not None:
            self._on_constant(value)
        elif action_type == "equals":
            self._on_equals()
        elif action_type == "backspace":
            self._on_backspace()
        elif action_type == "clear":
            self._on_clear()
        elif action_type == "all_clear":
            self._on_all_clear()
        elif action_type == "copy":
            self._copy_to_clipboard()
        elif action_type == "paste":
            self._paste_from_clipboard()
        elif action_type == "select_all":
            self._select_all()
