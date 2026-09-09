"""
main.py
=======
Modern Desktop Scientific Calculator Application.
Built with Python 3 and CustomTkinter.

Key Features:
- Clean modular structure separating UI from logic
- Standard and Scientific calculation modes
- Angle unit switching: Degrees (DEG) and Radians (RAD)
- Calculation history drawer with reloadable past results
- Memory functions (MC, MR, M+, M-, MS)
- Seamless Dark and Light theme toggling
- Full keyboard shortcut support
"""

import os
import sys
import customtkinter as ctk

# Ensure current directory is in path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from calculator import CalculatorEngine
from history import HistoryManager
from theme import Theme, Fonts, ThemeManager


class ScientificCalculatorApp(ctk.CTk):
    """
    Main desktop window for the Scientific Calculator.
    Handles GUI layout, event binding, and updates, delegating
    all calculations to the CalculatorEngine.
    """

    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------------------
        # 1. Logic & State Setup
        # ---------------------------------------------------------------------
        self.history_mgr = HistoryManager()
        self.engine = CalculatorEngine(history_manager=self.history_mgr)
        self.theme_mgr = ThemeManager(initial_mode="dark")
        self.is_scientific_mode = True
        self.is_history_open = False

        # ---------------------------------------------------------------------
        # 2. Window Configuration
        # ---------------------------------------------------------------------
        self.title("Scientific Calculator")
        self.set_window_icon()
        self.configure(fg_color=Theme.WINDOW_BG)
        self.resizable(True, True)

        # ---------------------------------------------------------------------
        # 3. Layout Construction
        # ---------------------------------------------------------------------
        self._build_ui()
        self._bind_keyboard_shortcuts()
        self._update_display()
        self._set_mode_geometry()

    def set_window_icon(self) -> None:
        """Sets window icon if the icon file exists."""
        ico_path = os.path.join(current_dir, "assets", "icons", "calculator.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # UI Layout Construction
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        """Constructs all visual components of the calculator."""
        # Root container: 2 columns (Left: Calculator, Right: History Panel)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Main Calculator Container
        self.calc_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calc_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.calc_frame.grid_columnconfigure(0, weight=1)

        # 1. Header Toolbar
        self._build_header(self.calc_frame)

        # 2. Display Screen
        self._build_display(self.calc_frame)

        # 3. Memory Bar
        self._build_memory_bar(self.calc_frame)

        # 4. Keypad Container (Scientific + Standard)
        self.keypad_frame = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        self.keypad_frame.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        self.calc_frame.grid_rowconfigure(3, weight=1)

        self._build_keypad(self.keypad_frame)

        # 5. Collapsible History Panel (Column 1)
        self._build_history_panel()

    def _build_header(self, parent: ctk.CTkFrame) -> None:
        """Builds top toolbar containing Mode selector, Angle toggle, and Themes."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Mode Selector: Standard vs Scientific
        self.mode_selector = ctk.CTkSegmentedButton(
            header_frame,
            values=["Standard", "Scientific"],
            command=self._on_mode_change,
            font=Fonts.button_memory(),
            selected_color="#1A73E8",
            selected_hover_color="#1558B0",
            unselected_color=Theme.BTN_TOOL["fg_color"],
            unselected_hover_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.TEXT_PRIMARY,
        )
        self.mode_selector.set("Scientific")
        self.mode_selector.grid(row=0, column=0, sticky="w")

        # Right buttons container
        right_tools = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_tools.grid(row=0, column=2, sticky="e")

        # Angle Unit Toggle (DEG / RAD)
        self.deg_rad_btn = ctk.CTkButton(
            right_tools,
            text="DEG",
            width=50,
            height=30,
            command=self._toggle_angle_mode,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.deg_rad_btn.pack(side="left", padx=4)

        # Theme Switcher (Dark / Light)
        self.theme_btn = ctk.CTkButton(
            right_tools,
            text="☀️",
            width=36,
            height=30,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=14),
            **Theme.BTN_TOOL,
        )
        self.theme_btn.pack(side="left", padx=4)

        # History Drawer Toggle Button
        self.history_btn = ctk.CTkButton(
            right_tools,
            text="🕒",
            width=36,
            height=30,
            command=self._toggle_history_panel,
            font=ctk.CTkFont(size=14),
            **Theme.BTN_TOOL,
        )
        self.history_btn.pack(side="left", padx=(4, 0))

    def _build_display(self, parent: ctk.CTkFrame) -> None:
        """Builds formula preview, status badges, and main result display."""
        self.display_frame = ctk.CTkFrame(
            parent,
            fg_color=Theme.DISPLAY_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.display_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.display_frame.grid_columnconfigure(0, weight=1)

        # Top line: Status Indicators + Formula Preview
        status_line = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        status_line.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 2))
        status_line.grid_columnconfigure(1, weight=1)

        # Indicators (e.g. DEG, M)
        self.indicator_label = ctk.CTkLabel(
            status_line,
            text="DEG",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ACCENT,
            anchor="w",
        )
        self.indicator_label.grid(row=0, column=0, sticky="w")

        # Formula / Previous expression label
        self.formula_label = ctk.CTkLabel(
            status_line,
            text="",
            font=Fonts.display_formula(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="e",
        )
        self.formula_label.grid(row=0, column=1, sticky="e")

        # Primary Result Readout
        self.result_label = ctk.CTkLabel(
            self.display_frame,
            text="0",
            font=Fonts.display_result(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="e",
        )
        self.result_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(2, 14))

    def _build_memory_bar(self, parent: ctk.CTkFrame) -> None:
        """Builds memory control buttons (MC, MR, M+, M-, MS)."""
        mem_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mem_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        memory_buttons = [
            ("MC", self._on_mc),
            ("MR", self._on_mr),
            ("M+", self._on_m_add),
            ("M-", self._on_m_sub),
            ("MS", self._on_ms),
        ]

        for col, (label, cmd) in enumerate(memory_buttons):
            mem_frame.grid_columnconfigure(col, weight=1)
            btn = ctk.CTkButton(
                mem_frame,
                text=label,
                height=26,
                command=cmd,
                font=Fonts.button_memory(),
                **Theme.BTN_MEMORY,
            )
            btn.grid(row=0, column=col, padx=2, sticky="ew")

    def _build_keypad(self, parent: ctk.CTkFrame) -> None:
        """Constructs standard and scientific key grids."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # Scientific Keys Frame
        self.sci_keys_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.sci_keys_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        # Scientific Button Matrix (5 cols x 4 rows)
        sci_buttons = [
            # Row 0
            [("sin", lambda: self._on_func("sin")),
             ("cos", lambda: self._on_func("cos")),
             ("tan", lambda: self._on_func("tan")),
             ("π", lambda: self._on_constant("pi")),
             ("e", lambda: self._on_constant("e"))],
            # Row 1
            [("asin", lambda: self._on_func("asin")),
             ("acos", lambda: self._on_func("acos")),
             ("atan", lambda: self._on_func("atan")),
             ("ln", lambda: self._on_func("ln")),
             ("log", lambda: self._on_func("log10"))],
            # Row 2
            [("x²", lambda: self._on_unary("sqr")),
             ("x³", lambda: self._on_unary("cube")),
             ("xʸ", lambda: self._on_operator("^")),
             ("√x", lambda: self._on_func("sqrt")),
             ("∛x", lambda: self._on_func("cbrt"))],
            # Row 3
            [("n!", lambda: self._on_unary("fact")),
             ("1/x", lambda: self._on_unary("recip")),
             ("|x|", lambda: self._on_func("abs")),
             ("(", lambda: self._on_bracket("(")),
             (")", lambda: self._on_bracket(")"))],
        ]

        for r, row in enumerate(sci_buttons):
            self.sci_keys_frame.grid_rowconfigure(r, weight=1)
            for c, (text, action) in enumerate(row):
                self.sci_keys_frame.grid_columnconfigure(c, weight=1)
                btn = ctk.CTkButton(
                    self.sci_keys_frame,
                    text=text,
                    height=40,
                    command=action,
                    font=Fonts.button_scientific(),
                    **Theme.BTN_SCIENTIFIC,
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

        # Standard Keypad Frame (4 cols x 5 rows)
        self.std_keys_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.std_keys_frame.grid(row=1, column=0, sticky="nsew")

        for c in range(4):
            self.std_keys_frame.grid_columnconfigure(c, weight=1)

        std_layout = [
            # Row 0: Actions & Division
            [("AC", self._on_all_clear, Theme.BTN_ACTION, Fonts.button_main()),
             ("C", self._on_clear, Theme.BTN_ACTION, Fonts.button_main()),
             ("⌫", self._on_backspace, Theme.BTN_ACTION, Fonts.button_main()),
             ("÷", lambda: self._on_operator("/"), Theme.BTN_OPERATOR, Fonts.button_main())],

            # Row 1: 7, 8, 9, ×
            [("7", lambda: self._on_number("7"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("8", lambda: self._on_number("8"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("9", lambda: self._on_number("9"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("×", lambda: self._on_operator("*"), Theme.BTN_OPERATOR, Fonts.button_main())],

            # Row 2: 4, 5, 6, -
            [("4", lambda: self._on_number("4"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("5", lambda: self._on_number("5"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("6", lambda: self._on_number("6"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("-", lambda: self._on_operator("-"), Theme.BTN_OPERATOR, Fonts.button_main())],

            # Row 3: 1, 2, 3, +
            [("1", lambda: self._on_number("1"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("2", lambda: self._on_number("2"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("3", lambda: self._on_number("3"), Theme.BTN_NUMBER, Fonts.button_main()),
             ("+", lambda: self._on_operator("+"), Theme.BTN_OPERATOR, Fonts.button_main())],

            # Row 4: ±, 0, ., =
            [("±", self._on_toggle_sign, Theme.BTN_NUMBER, Fonts.button_main()),
             ("0", lambda: self._on_number("0"), Theme.BTN_NUMBER, Fonts.button_main()),
             (".", self._on_decimal, Theme.BTN_NUMBER, Fonts.button_main()),
             ("=", self._on_equals, Theme.BTN_EQUALS, Fonts.button_main())],
        ]

        for r, row in enumerate(std_layout):
            self.std_keys_frame.grid_rowconfigure(r, weight=1)
            for c, (text, action, styling, font) in enumerate(row):
                btn = ctk.CTkButton(
                    self.std_keys_frame,
                    text=text,
                    height=48,
                    command=action,
                    font=font,
                    **styling,
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

    def _build_history_panel(self) -> None:
        """Constructs the slide-out history panel on the right side."""
        self.history_frame = ctk.CTkFrame(
            self,
            fg_color=Theme.PANEL_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
            width=260,
        )
        # Hidden by default

        # History Header
        header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 6))

        title = ctk.CTkLabel(
            header,
            text="History",
            font=Fonts.history_title(),
            text_color=Theme.TEXT_PRIMARY,
        )
        title.pack(side="left")

        clear_btn = ctk.CTkButton(
            header,
            text="Clear",
            width=50,
            height=26,
            command=self._clear_history,
            font=Fonts.button_memory(),
            **Theme.BTN_ACTION,
        )
        clear_btn.pack(side="right")

        # Scrollable area for entries
        self.history_scroll = ctk.CTkScrollableFrame(
            self.history_frame,
            fg_color="transparent",
        )
        self.history_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # -------------------------------------------------------------------------
    # Display & State Synchronization
    # -------------------------------------------------------------------------
    def _update_display(self) -> None:
        """Refreshes the formula label, result readout, and status badges."""
        self.formula_label.configure(text=self.engine.previous_expression)

        # Dynamic font scaling if the result is very long
        text = self.engine.current_input
        if len(text) > 16:
            font_size = 20
        elif len(text) > 12:
            font_size = 24
        else:
            font_size = 32
        self.result_label.configure(
            text=text,
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=font_size, weight="bold"),
        )

        # Update indicators
        mem_flag = " | M" if self.engine.has_memory else ""
        self.indicator_label.configure(text=f"{self.engine.angle_mode}{mem_flag}")
        self.deg_rad_btn.configure(text=self.engine.angle_mode)

    def _refresh_history_list(self) -> None:
        """Populates the history scroll frame with current history records."""
        # Clear existing widgets
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        entries = self.history_mgr.get_all()
        if not entries:
            empty_lbl = ctk.CTkLabel(
                self.history_scroll,
                text="No calculations yet.",
                font=Fonts.history_item(),
                text_color=Theme.TEXT_SECONDARY,
            )
            empty_lbl.pack(pady=30)
            return

        for entry in entries:
            # Entry Card
            card = ctk.CTkFrame(
                self.history_scroll,
                fg_color=Theme.DISPLAY_BG,
                corner_radius=8,
                border_width=1,
                border_color=Theme.BORDER_COLOR,
            )
            card.pack(fill="x", pady=4, padx=2)

            # Click handler to load calculation
            def make_loader(e=entry):
                return lambda event=None: self._load_history_entry(e)

            card.bind("<Button-1>", make_loader())

            time_lbl = ctk.CTkLabel(
                card,
                text=entry.timestamp,
                font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=9),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            time_lbl.pack(fill="x", padx=10, pady=(6, 0))
            time_lbl.bind("<Button-1>", make_loader())

            expr_lbl = ctk.CTkLabel(
                card,
                text=entry.expression,
                font=Fonts.history_item(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="e",
            )
            expr_lbl.pack(fill="x", padx=10, pady=1)
            expr_lbl.bind("<Button-1>", make_loader())

            res_lbl = ctk.CTkLabel(
                card,
                text=f"= {entry.result}",
                font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=15, weight="bold"),
                text_color=Theme.TEXT_ACCENT,
                anchor="e",
            )
            res_lbl.pack(fill="x", padx=10, pady=(1, 6))
            res_lbl.bind("<Button-1>", make_loader())

    def _load_history_entry(self, entry) -> None:
        """Loads a past calculation result into the calculator input."""
        self.engine.current_input = entry.result
        self.engine.previous_expression = f"{entry.expression} ="
        self.engine.is_new_calculation = True
        self._update_display()

    def _clear_history(self) -> None:
        """Clears all stored history."""
        self.history_mgr.clear()
        self._refresh_history_list()

    # -------------------------------------------------------------------------
    # Button Action Handlers
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
        if self.is_history_open:
            self._refresh_history_list()

    def _on_toggle_sign(self) -> None:
        self.engine.toggle_sign()
        self._update_display()

    def _on_equals(self) -> None:
        self.engine.calculate()
        self._update_display()
        if self.is_history_open:
            self._refresh_history_list()

    def _on_backspace(self) -> None:
        self.engine.backspace()
        self._update_display()

    def _on_clear(self) -> None:
        self.engine.clear()
        self._update_display()

    def _on_all_clear(self) -> None:
        self.engine.all_clear()
        self._update_display()

    # Memory actions
    def _on_mc(self) -> None:
        self.engine.memory_clear()
        self._update_display()

    def _on_mr(self) -> None:
        self.engine.memory_recall()
        self._update_display()

    def _on_m_add(self) -> None:
        self.engine.memory_add()
        self._update_display()

    def _on_m_sub(self) -> None:
        self.engine.memory_subtract()
        self._update_display()

    def _on_ms(self) -> None:
        self.engine.memory_store()
        self._update_display()

    # Header actions
    def _toggle_angle_mode(self) -> None:
        new_mode = self.engine.toggle_angle_mode()
        self.deg_rad_btn.configure(text=new_mode)
        self._update_display()

    def _toggle_theme(self) -> None:
        new_mode = self.theme_mgr.toggle()
        self.theme_btn.configure(text="🌙" if new_mode == "light" else "☀️")

    def _toggle_history_panel(self) -> None:
        self.is_history_open = not self.is_history_open
        if self.is_history_open:
            self._refresh_history_list()
            self.history_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        else:
            self.history_frame.grid_forget()
        self._set_mode_geometry()

    def _on_mode_change(self, mode_name: str) -> None:
        self.is_scientific_mode = (mode_name == "Scientific")
        if self.is_scientific_mode:
            self.sci_keys_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        else:
            self.sci_keys_frame.grid_forget()
        self._set_mode_geometry()

    def _set_mode_geometry(self) -> None:
        """Dynamically adjusts recommended window geometry based on active panels."""
        if self.is_scientific_mode:
            base_w = 440
            base_h = 650
        else:
            base_w = 360
            base_h = 490

        if self.is_history_open:
            base_w += 260

        self.minsize(340, 480)
        self.geometry(f"{base_w}x{base_h}")

    # -------------------------------------------------------------------------
    # Keyboard Shortcuts
    # -------------------------------------------------------------------------
    def _bind_keyboard_shortcuts(self) -> None:
        """Binds physical keyboard events to calculator actions."""
        # Numbers 0-9
        for digit in "0123456789":
            self.bind(digit, lambda event, d=digit: self._on_number(d))
            self.bind(f"<KP_{digit}>", lambda event, d=digit: self._on_number(d))

        # Basic Operators
        self.bind("+", lambda event: self._on_operator("+"))
        self.bind("-", lambda event: self._on_operator("-"))
        self.bind("*", lambda event: self._on_operator("*"))
        self.bind("/", lambda event: self._on_operator("/"))
        self.bind("^", lambda event: self._on_operator("^"))
        self.bind(".", lambda event: self._on_decimal())

        # Parentheses
        self.bind("(", lambda event: self._on_bracket("("))
        self.bind(")", lambda event: self._on_bracket(")"))

        # Equals / Enter
        self.bind("<Return>", lambda event: self._on_equals())
        self.bind("<KP_Enter>", lambda event: self._on_equals())
        self.bind("=", lambda event: self._on_equals())

        # Delete & Backspace
        self.bind("<BackSpace>", lambda event: self._on_backspace())
        self.bind("<Delete>", lambda event: self._on_clear())
        self.bind("<Escape>", lambda event: self._on_all_clear())

        # Shortcuts for common scientific constants
        self.bind("p", lambda event: self._on_constant("pi"))
        self.bind("P", lambda event: self._on_constant("pi"))


def main():
    """Application entry point."""
    app = ScientificCalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
