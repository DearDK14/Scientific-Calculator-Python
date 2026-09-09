"""
main.py
=======
Modern Desktop Scientific Calculator Application.
Built with Python 3 and CustomTkinter.

Layout:
-------
Top:
    Expression display
    Result display

Scientific section (3 cols x 5 rows):
    sin  cos  tan
    asin acos atan
    log  ln   √
    x²   xʸ   π
    e    !    %

Main keypad (4 cols x 4 rows):
    7 8 9 ÷
    4 5 6 ×
    1 2 3 −
    0 . ± +

Bottom (5 cols x 1 row):
    C DEL ( ) =
"""

import os
import sys
import customtkinter as ctk

# Ensure current directory is in search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from calculator import CalculatorEngine
from history import HistoryManager
from theme import Theme, Fonts, ThemeManager


class ScientificCalculatorApp(ctk.CTk):
    """
    Main desktop window for the Modern Scientific Calculator.
    Provides a dark modern interface with responsive layout and clear
    visual distinction between button types.
    """

    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------------------
        # 1. Logic & State Setup
        # ---------------------------------------------------------------------
        self.history_mgr = HistoryManager()
        self.engine = CalculatorEngine(history_manager=self.history_mgr)
        self.theme_mgr = ThemeManager(initial_mode="dark")

        # ---------------------------------------------------------------------
        # 2. Window Configuration
        # ---------------------------------------------------------------------
        self.title("Scientific Calculator")
        self._set_window_icon()
        self.configure(fg_color=Theme.WINDOW_BG)
        self.geometry("440x720")
        self.minsize(360, 600)
        self.resizable(True, True)

        # ---------------------------------------------------------------------
        # 3. Layout Construction
        # ---------------------------------------------------------------------
        self._build_ui()
        self._bind_keyboard_shortcuts()
        self._update_display()

    def _set_window_icon(self) -> None:
        """Sets application window icon if available."""
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
        """Constructs all visual components with proper responsive spacing."""
        # Configure root grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main wrapper container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=18, pady=16)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Container row distribution:
        # Row 0: Top Bar (DEG/RAD, Title, Theme)
        # Row 1: Display Box (Expression + Result)
        # Row 2: Scientific Section (3x5)
        # Row 3: Main Keypad (4x4)
        # Row 4: Bottom Row (5x1)
        self.main_container.grid_rowconfigure(0, weight=0)  # Top Bar
        self.main_container.grid_rowconfigure(1, weight=0)  # Display
        self.main_container.grid_rowconfigure(2, weight=5)  # Scientific
        self.main_container.grid_rowconfigure(3, weight=5)  # Main Keypad
        self.main_container.grid_rowconfigure(4, weight=1)  # Bottom Row

        # 1. Top Header Bar
        self._build_top_bar(self.main_container)

        # 2. Display Section (Expression + Result)
        self._build_display(self.main_container)

        # 3. Scientific Section (3 cols x 5 rows)
        self._build_scientific_section(self.main_container)

        # 4. Main Keypad (4 cols x 4 rows)
        self._build_main_keypad(self.main_container)

        # 5. Bottom Row (5 cols x 1 row)
        self._build_bottom_row(self.main_container)

    def _build_top_bar(self, parent: ctk.CTkFrame) -> None:
        """Builds a minimal, clean top bar with DEG/RAD and theme controls."""
        top_bar = ctk.CTkFrame(parent, fg_color="transparent", height=32)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_bar.grid_columnconfigure(1, weight=1)

        # DEG / RAD Toggle Button
        self.deg_rad_btn = ctk.CTkButton(
            top_bar,
            text="DEG",
            width=54,
            height=28,
            command=self._toggle_angle_mode,
            font=Fonts.label_badge(),
            **Theme.BTN_TOOL,
        )
        self.deg_rad_btn.grid(row=0, column=0, sticky="w")

        # Subtle Title / Branding
        title_label = ctk.CTkLabel(
            top_bar,
            text="SCIENTIFIC",
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_SECONDARY,
        )
        title_label.grid(row=0, column=1)

        # Dark / Light Theme Toggle Button
        self.theme_btn = ctk.CTkButton(
            top_bar,
            text="☀️",
            width=36,
            height=28,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=13),
            **Theme.BTN_TOOL,
        )
        self.theme_btn.grid(row=0, column=2, sticky="e")

    def _build_display(self, parent: ctk.CTkFrame) -> None:
        """
        Builds the primary calculation display.
        Contains a smaller expression/history display above the large result readout.
        """
        self.display_card = ctk.CTkFrame(
            parent,
            fg_color=Theme.DISPLAY_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=14,
        )
        self.display_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.display_card.grid_columnconfigure(0, weight=1)

        # Smaller Expression / History Display
        self.expression_label = ctk.CTkLabel(
            self.display_card,
            text="",
            font=Fonts.display_formula(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="e",
        )
        self.expression_label.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 2))

        # Large Primary Result Display
        self.result_label = ctk.CTkLabel(
            self.display_card,
            text="0",
            font=Fonts.display_result(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="e",
        )
        self.result_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(2, 14))

    def _build_scientific_section(self, parent: ctk.CTkFrame) -> None:
        """
        Scientific section: 3 columns x 5 rows
        sin  cos  tan
        asin acos atan
        log  ln   √
        x²   xʸ   π
        e    !    %
        """
        self.sci_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.sci_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 8))

        # 3 columns with equal expansion
        for c in range(3):
            self.sci_frame.grid_columnconfigure(c, weight=1)

        # 5 rows
        sci_buttons = [
            # Row 0
            [("sin", lambda: self._on_func("sin")),
             ("cos", lambda: self._on_func("cos")),
             ("tan", lambda: self._on_func("tan"))],
            # Row 1
            [("asin", lambda: self._on_func("asin")),
             ("acos", lambda: self._on_func("acos")),
             ("atan", lambda: self._on_func("atan"))],
            # Row 2
            [("log", lambda: self._on_func("log10")),
             ("ln", lambda: self._on_func("ln")),
             ("√", lambda: self._on_func("sqrt"))],
            # Row 3
            [("x²", lambda: self._on_unary("sqr")),
             ("xʸ", lambda: self._on_operator("^")),
             ("π", lambda: self._on_constant("pi"))],
            # Row 4
            [("e", lambda: self._on_constant("e")),
             ("!", lambda: self._on_unary("fact")),
             ("%", lambda: self._on_unary("percent"))],
        ]

        for r, row in enumerate(sci_buttons):
            self.sci_frame.grid_rowconfigure(r, weight=1)
            for c, (label, cmd) in enumerate(row):
                btn = ctk.CTkButton(
                    self.sci_frame,
                    text=label,
                    command=cmd,
                    font=Fonts.button_scientific(),
                    **Theme.BTN_SCIENTIFIC,
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

    def _build_main_keypad(self, parent: ctk.CTkFrame) -> None:
        """
        Main keypad: 4 columns x 4 rows
        7 8 9 ÷
        4 5 6 ×
        1 2 3 −
        0 . ± +
        """
        self.main_keypad = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_keypad.grid(row=3, column=0, sticky="nsew", pady=(0, 8))

        # 4 columns with equal expansion
        for c in range(4):
            self.main_keypad.grid_columnconfigure(c, weight=1)

        main_buttons = [
            # Row 0: 7 8 9 ÷
            [("7", lambda: self._on_number("7"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("8", lambda: self._on_number("8"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("9", lambda: self._on_number("9"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("÷", lambda: self._on_operator("/"), Theme.BTN_OPERATOR, Fonts.button_operator())],

            # Row 1: 4 5 6 ×
            [("4", lambda: self._on_number("4"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("5", lambda: self._on_number("5"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("6", lambda: self._on_number("6"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("×", lambda: self._on_operator("*"), Theme.BTN_OPERATOR, Fonts.button_operator())],

            # Row 2: 1 2 3 −
            [("1", lambda: self._on_number("1"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("2", lambda: self._on_number("2"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("3", lambda: self._on_number("3"), Theme.BTN_NUMBER, Fonts.button_number()),
             ("−", lambda: self._on_operator("-"), Theme.BTN_OPERATOR, Fonts.button_operator())],

            # Row 3: 0 . ± +
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

    def _build_bottom_row(self, parent: ctk.CTkFrame) -> None:
        """
        Bottom: 5 columns x 1 row
        C DEL ( ) =
        """
        self.bottom_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.bottom_frame.grid(row=4, column=0, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)

        # 5 columns with equal expansion
        for c in range(5):
            self.bottom_frame.grid_columnconfigure(c, weight=1)

        bottom_buttons = [
            ("C", self._on_clear, Theme.BTN_ACTION, Fonts.button_bottom()),
            ("DEL", self._on_backspace, Theme.BTN_ACTION, Fonts.button_bottom()),
            ("(", lambda: self._on_bracket("("), Theme.BTN_BRACKET, Fonts.button_bottom()),
            (")", lambda: self._on_bracket(")"), Theme.BTN_BRACKET, Fonts.button_bottom()),
            ("=", self._on_equals, Theme.BTN_EQUALS, Fonts.button_operator()),
        ]

        for c, (label, cmd, styling, font) in enumerate(bottom_buttons):
            btn = ctk.CTkButton(
                self.bottom_frame,
                text=label,
                command=cmd,
                font=font,
                **styling,
            )
            btn.grid(row=0, column=c, padx=3, pady=3, sticky="nsew")

    # -------------------------------------------------------------------------
    # Display Updates & Auto-Scaling
    # -------------------------------------------------------------------------
    def _update_display(self) -> None:
        """Refreshes expression and result readouts with dynamic font scaling."""
        self.expression_label.configure(text=self.engine.previous_expression)

        text = self.engine.current_input
        # Responsive font scaling for long results to avoid truncation
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
        self.deg_rad_btn.configure(text=self.engine.angle_mode)

    # -------------------------------------------------------------------------
    # Button Event Handlers
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

    def _toggle_angle_mode(self) -> None:
        new_mode = self.engine.toggle_angle_mode()
        self.deg_rad_btn.configure(text=new_mode)
        self._update_display()

    def _toggle_theme(self) -> None:
        new_mode = self.theme_mgr.toggle()
        self.theme_btn.configure(text="🌙" if new_mode == "light" else "☀️")

    # -------------------------------------------------------------------------
    # Keyboard Event Bindings
    # -------------------------------------------------------------------------
    def _bind_keyboard_shortcuts(self) -> None:
        """Binds physical keyboard keys to calculator actions."""
        # Numbers 0-9
        for digit in "0123456789":
            self.bind(digit, lambda event, d=digit: self._on_number(d))
            self.bind(f"<KP_{digit}>", lambda event, d=digit: self._on_number(d))

        # Basic Operators
        self.bind("+", lambda event: self._on_operator("+"))
        self.bind("<KP_Add>", lambda event: self._on_operator("+"))
        self.bind("-", lambda event: self._on_operator("-"))
        self.bind("<KP_Subtract>", lambda event: self._on_operator("-"))
        self.bind("*", lambda event: self._on_operator("*"))
        self.bind("<KP_Multiply>", lambda event: self._on_operator("*"))
        self.bind("/", lambda event: self._on_operator("/"))
        self.bind("<KP_Divide>", lambda event: self._on_operator("/"))
        self.bind("^", lambda event: self._on_operator("^"))
        self.bind(".", lambda event: self._on_decimal())
        self.bind("<KP_Decimal>", lambda event: self._on_decimal())
        self.bind("%", lambda event: self._on_unary("percent"))
        self.bind("!", lambda event: self._on_unary("fact"))

        # Parentheses
        self.bind("(", lambda event: self._on_bracket("("))
        self.bind(")", lambda event: self._on_bracket(")"))

        # Equals / Enter (bind_all ensures it triggers even when a button has focus)
        self.bind_all("<Return>", lambda event: self._on_equals())
        self.bind_all("<KP_Enter>", lambda event: self._on_equals())
        self.bind("=", lambda event: self._on_equals())

        # Clear & Delete
        self.bind_all("<BackSpace>", lambda event: self._on_backspace())
        self.bind_all("<Delete>", lambda event: self._on_clear())
        self.bind_all("<Escape>", lambda event: self._on_clear())
        self.bind("c", lambda event: self._on_clear())
        self.bind("C", lambda event: self._on_clear())

        # Mathematical constants
        self.bind("p", lambda event: self._on_constant("pi"))
        self.bind("P", lambda event: self._on_constant("pi"))
        self.bind("e", lambda event: self._on_constant("e"))
        self.bind("E", lambda event: self._on_constant("e"))


def main():
    """Application entry point."""
    app = ScientificCalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
