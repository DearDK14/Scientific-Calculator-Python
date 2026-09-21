"""
main.py
=======
Modern Desktop Scientific Calculator Application.
Built with Python 3 and CustomTkinter.

Features:
---------
1. Complete Scientific & Basic Calculation Support (PEMDAS, Safe AST)
2. Calculation History System on the Right Side (Loaded from JSON, Click-to-Load, Clear)
3. Full Keyboard Support (0-9, +, -, *, /, %, (), ., Enter, Backspace, Escape)
4. Clipboard System (Copy Button, Ctrl+C, Ctrl+V with sanitization, Visual Feedback)
5. Dark & Light Theme Support with DEG/RAD Angle Modes
"""

import os
import re
import sys
import customtkinter as ctk

# Ensure current directory is in search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from calculator import CalculatorEngine
from history import HistoryManager, HistoryEntry
from theme import Theme, Fonts, ThemeManager


class ScientificCalculatorApp(ctk.CTk):
    """
    Main desktop window for the Modern Scientific Calculator.
    Provides responsive layout, right-side history panel, full keyboard shortcuts,
    and safe clipboard support with visual confirmation.
    """

    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------------------
        # 1. State & Logic Setup
        # ---------------------------------------------------------------------
        self.history_mgr = HistoryManager(max_entries=50)
        self.engine = CalculatorEngine(history_manager=self.history_mgr)
        self.theme_mgr = ThemeManager(initial_mode="dark")
        self.is_history_open = True
        self._copied_timer = None
        self._paste_timer = None

        # ---------------------------------------------------------------------
        # 2. Window Configuration
        # ---------------------------------------------------------------------
        self.title("Scientific Calculator")
        self._set_window_icon()
        self.configure(fg_color=Theme.WINDOW_BG)
        self.geometry("750x760")
        self.minsize(680, 640)
        self.resizable(True, True)

        # ---------------------------------------------------------------------
        # 3. Layout Construction
        # ---------------------------------------------------------------------
        self._build_ui()
        self._bind_keyboard_shortcuts()
        self._update_display()
        self._refresh_history_list()

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
        """Constructs 2-column layout: Left = Calculator, Right = History Panel."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Calculator Frame
        self.calc_container = ctk.CTkFrame(self, fg_color="transparent")
        self.calc_container.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        self.calc_container.grid_columnconfigure(0, weight=1)

        # Row distribution for calculator container
        self.calc_container.grid_rowconfigure(0, weight=0)  # Top Bar
        self.calc_container.grid_rowconfigure(1, weight=0)  # Display Card
        self.calc_container.grid_rowconfigure(2, weight=6)  # Scientific Keys (6 rows)
        self.calc_container.grid_rowconfigure(3, weight=5)  # Main Keypad (4 rows)
        self.calc_container.grid_rowconfigure(4, weight=1)  # Bottom Row (1 row)

        # Build calculator sections
        self._build_top_bar(self.calc_container)
        self._build_display(self.calc_container)
        self._build_scientific_section(self.calc_container)
        self._build_main_keypad(self.calc_container)
        self._build_bottom_row(self.calc_container)

        # Right Column: History Panel
        self._build_history_panel()

    def _build_top_bar(self, parent: ctk.CTkFrame) -> None:
        """Top bar with DEG/RAD switch, Title, History toggle, and Theme switch."""
        top_bar = ctk.CTkFrame(parent, fg_color="transparent", height=32)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_bar.grid_columnconfigure(1, weight=1)

        # DEG / RAD Toggle
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

        # Title
        title_label = ctk.CTkLabel(
            top_bar,
            text="SCIENTIFIC",
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_SECONDARY,
        )
        title_label.grid(row=0, column=1)

        # Right-side tool buttons (History Toggle + Theme)
        right_tools = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_tools.grid(row=0, column=2, sticky="e")

        # History Panel Toggle Button
        self.history_toggle_btn = ctk.CTkButton(
            right_tools,
            text="🕒 History",
            width=80,
            height=28,
            command=self._toggle_history_panel,
            font=Fonts.label_badge(),
            fg_color=Theme.BTN_TOOL["hover_color"] if self.is_history_open else Theme.BTN_TOOL["fg_color"],
            hover_color=Theme.BTN_TOOL["hover_color"],
            text_color=Theme.TEXT_ACCENT if self.is_history_open else Theme.BTN_TOOL["text_color"],
            corner_radius=8,
        )
        self.history_toggle_btn.pack(side="left", padx=(0, 6))

        # Dark / Light Theme Toggle
        self.theme_btn = ctk.CTkButton(
            right_tools,
            text="☀️",
            width=36,
            height=28,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=13),
            **Theme.BTN_TOOL,
        )
        self.theme_btn.pack(side="left")

    def _build_display(self, parent: ctk.CTkFrame) -> None:
        """
        Calculation display card:
        - Header with angle mode badge and dedicated Copy button with feedback.
        - Smaller expression/history line.
        - Large prominent result line.
        """
        self.display_card = ctk.CTkFrame(
            parent,
            fg_color=Theme.DISPLAY_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=14,
        )
        self.display_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.display_card.grid_columnconfigure(0, weight=1)

        # Display Top Utility Line (Badge + Copy Button)
        disp_header = ctk.CTkFrame(self.display_card, fg_color="transparent")
        disp_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
        disp_header.grid_columnconfigure(1, weight=1)

        # Status Badge (DEG / RAD)
        self.badge_label = ctk.CTkLabel(
            disp_header,
            text="DEG",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ACCENT,
            anchor="w",
        )
        self.badge_label.grid(row=0, column=0, sticky="w")

        # Copy Notification / Action Container
        copy_box = ctk.CTkFrame(disp_header, fg_color="transparent")
        copy_box.grid(row=0, column=2, sticky="e")

        # Feedback Toast Label (for Copy & Paste events)
        self.feedback_label = ctk.CTkLabel(
            copy_box,
            text="",
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_SUCCESS,
            anchor="e",
        )
        self.feedback_label.pack(side="left", padx=(0, 6))

        # Copy Button
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

        # Smaller Expression / History Display
        self.expression_label = ctk.CTkLabel(
            self.display_card,
            text="",
            font=Fonts.display_formula(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="e",
        )
        self.expression_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 2))

        # Large Primary Result Display
        self.result_label = ctk.CTkLabel(
            self.display_card,
            text="0",
            font=Fonts.display_result(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="e",
        )
        self.result_label.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 12))

    def _build_scientific_section(self, parent: ctk.CTkFrame) -> None:
        """Scientific Section (3 columns x 6 rows)"""
        self.sci_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.sci_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 8))

        for c in range(3):
            self.sci_frame.grid_columnconfigure(c, weight=1)

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
             ("√", self._on_sqrt)],
            # Row 3
            [("x²", lambda: self._on_unary("sqr")),
             ("xʸ", lambda: self._on_operator("^")),
             ("π", lambda: self._on_constant("pi"))],
            # Row 4
            [("e", lambda: self._on_constant("e")),
             ("!", lambda: self._on_unary("fact")),
             ("%", lambda: self._on_unary("percent"))],
            # Row 5
            [("exp", self._on_exp),
             ("1/x", lambda: self._on_unary("recip")),
             ("|x|", lambda: self._on_unary("abs"))],
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
        """Main Numeric & Arithmetic Keypad (4 columns x 4 rows)"""
        self.main_keypad = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_keypad.grid(row=3, column=0, sticky="nsew", pady=(0, 8))

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
        """Bottom Actions Row (5 columns x 1 row): C DEL ( ) ="""
        self.bottom_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.bottom_frame.grid(row=4, column=0, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)

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
    # History Panel Construction
    # -------------------------------------------------------------------------
    def _build_history_panel(self) -> None:
        """
        Builds the History Panel on the right side:
        ------------------
        History
        ------------------
        25 × 4 = 100
        sin(30) = 0.5
        √144 = 12
        100 ÷ 4 = 25
        ------------------
        Clear History
        """
        self.history_frame = ctk.CTkFrame(
            self,
            fg_color=Theme.PANEL_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=14,
            width=270,
        )
        self.history_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(2, weight=1)

        # Header Frame
        header = ctk.CTkFrame(self.history_frame, fg_color="transparent", height=32)
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="History",
            font=Fonts.history_title(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=26,
            height=26,
            command=self._toggle_history_panel,
            font=ctk.CTkFont(size=12, weight="bold"),
            **Theme.BTN_COPY,
        )
        close_btn.grid(row=0, column=1, sticky="e")

        # Top Divider Line
        top_divider = ctk.CTkFrame(self.history_frame, fg_color=Theme.DIVIDER_COLOR, height=1)
        top_divider.grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 6))

        # Scrollable Area for Entries
        self.history_scroll = ctk.CTkScrollableFrame(
            self.history_frame,
            fg_color="transparent",
        )
        self.history_scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=0)
        self.history_scroll.grid_columnconfigure(0, weight=1)

        # Bottom Divider Line
        bottom_divider = ctk.CTkFrame(self.history_frame, fg_color=Theme.DIVIDER_COLOR, height=1)
        bottom_divider.grid(row=3, column=0, sticky="ew", padx=12, pady=(6, 8))

        # Clear History Button
        self.clear_hist_btn = ctk.CTkButton(
            self.history_frame,
            text="Clear History",
            height=36,
            command=self._clear_history,
            font=Fonts.button_bottom(),
            **Theme.BTN_ACTION,
        )
        self.clear_hist_btn.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 14))

    def _refresh_history_list(self) -> None:
        """Populates scrollable history area with stored calculations."""
        # Clear existing card widgets
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        entries = self.history_mgr.get_all()
        if not entries:
            empty_box = ctk.CTkFrame(self.history_scroll, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=40)

            empty_lbl = ctk.CTkLabel(
                empty_box,
                text="No history yet\nPerform a calculation to see it here!",
                font=Fonts.history_expr(),
                text_color=Theme.TEXT_SECONDARY,
                justify="center",
            )
            empty_lbl.pack()
            return

        for entry in entries:
            # Individual History Card
            card = ctk.CTkFrame(
                self.history_scroll,
                fg_color=Theme.CARD_BG,
                border_color=Theme.BORDER_COLOR,
                border_width=1,
                corner_radius=10,
            )
            card.pack(fill="x", pady=4, padx=2)
            card.grid_columnconfigure(0, weight=1)

            # Click loader lambda
            def make_loader(e=entry):
                return lambda event=None: self._load_history_entry(e)

            card.bind("<Button-1>", make_loader())

            # Header timestamp
            time_lbl = ctk.CTkLabel(
                card,
                text=entry.timestamp,
                font=Fonts.history_time(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            time_lbl.pack(fill="x", padx=10, pady=(6, 1))
            time_lbl.bind("<Button-1>", make_loader())

            # Expression Line
            expr_lbl = ctk.CTkLabel(
                card,
                text=entry.expression,
                font=Fonts.history_expr(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="e",
            )
            expr_lbl.pack(fill="x", padx=10, pady=1)
            expr_lbl.bind("<Button-1>", make_loader())

            # Result Line
            res_lbl = ctk.CTkLabel(
                card,
                text=f"= {entry.result}",
                font=Fonts.history_result(),
                text_color=Theme.TEXT_ACCENT,
                anchor="e",
            )
            res_lbl.pack(fill="x", padx=10, pady=(1, 8))
            res_lbl.bind("<Button-1>", make_loader())

    def _load_history_entry(self, entry: HistoryEntry) -> None:
        """Loads a previous calculation result into the calculator display."""
        self.engine.current_input = entry.result
        self.engine.previous_expression = f"{entry.expression} ="
        self.engine.is_new_calculation = True
        self._update_display()
        self._show_feedback("Loaded from history", Theme.TEXT_ACCENT)

    def _clear_history(self) -> None:
        """Clears all stored history records and updates view."""
        self.history_mgr.clear()
        self._refresh_history_list()
        self._show_feedback("History cleared", Theme.TEXT_SECONDARY)

    def _toggle_history_panel(self) -> None:
        """Toggles visibility of the right-side History panel."""
        self.is_history_open = not self.is_history_open
        if self.is_history_open:
            self._refresh_history_list()
            self.history_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
            self.history_toggle_btn.configure(
                fg_color=Theme.BTN_TOOL["hover_color"],
                text_color=Theme.TEXT_ACCENT,
            )
            self.geometry("750x760")
            self.minsize(680, 640)
        else:
            self.history_frame.grid_forget()
            self.history_toggle_btn.configure(
                fg_color=Theme.BTN_TOOL["fg_color"],
                text_color=Theme.BTN_TOOL["text_color"],
            )
            self.geometry("450x760")
            self.minsize(420, 640)

    # -------------------------------------------------------------------------
    # Clipboard Operations & Visual Feedback
    # -------------------------------------------------------------------------
    def _copy_to_clipboard(self, event=None) -> None:
        """
        Copies the current result/display value to the clipboard.
        Provides visual feedback on the Copy button.
        """
        text = self.engine.current_input.strip()
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()  # Finalize clipboard on Windows
            self._show_copied_feedback()
        except Exception as err:
            self._show_feedback(f"Copy failed: {err}", Theme.TEXT_SECONDARY)

    def _paste_from_clipboard(self, event=None) -> None:
        """
        Pastes mathematical expression from clipboard safely.
        Validates and sanitizes text to prevent crashes.
        """
        try:
            text = self.clipboard_get()
        except Exception:
            # Clipboard empty or non-text
            return

        if not text:
            return

        # Sanitize whitespace & newlines
        clean_text = text.strip().replace("\r", "").replace("\n", " ")

        # Validate allowed mathematical characters
        allowed_pattern = r"^[0-9+\-−×*÷/().%^!a-zA-Z\sπe|]+$"
        if not re.match(allowed_pattern, clean_text):
            self._show_feedback("Invalid paste content", Theme.BTN_ACTION["text_color"])
            return

        # Prevent giant strings that could freeze the UI
        if len(clean_text) > 120:
            clean_text = clean_text[:120]

        # Check if single number or expression
        try:
            float(clean_text)
            self.engine.current_input = clean_text
            self.engine.is_new_calculation = True
        except ValueError:
            self.engine.current_input = clean_text
            self.engine.is_new_calculation = False

        self._update_display()
        self._show_feedback("Pasted!", Theme.TEXT_SUCCESS)

    def _select_all(self, event=None) -> None:
        """Visually highlights the display card showing all text is selected."""
        self.display_card.configure(border_color="#38BDF8", border_width=2)
        self.after(400, lambda: self.display_card.configure(
            border_color=Theme.BORDER_COLOR, border_width=1
        ))

    def _show_copied_feedback(self) -> None:
        """Shows visual indication that current result was copied."""
        self.copy_btn.configure(text="✓ Copied!", text_color=Theme.TEXT_SUCCESS[0])
        self._show_feedback("Result copied", Theme.TEXT_SUCCESS)
        if self._copied_timer:
            self.after_cancel(self._copied_timer)
        self._copied_timer = self.after(1500, self._reset_copy_btn)

    def _reset_copy_btn(self) -> None:
        """Resets copy button text back to default."""
        self.copy_btn.configure(text="📋 Copy", text_color=Theme.BTN_COPY["text_color"])

    def _show_feedback(self, msg: str, color_tuple) -> None:
        """Displays temporary toast message next to the Copy button."""
        color = color_tuple[0] if isinstance(color_tuple, tuple) else color_tuple
        self.feedback_label.configure(text=msg, text_color=color)
        if self._paste_timer:
            self.after_cancel(self._paste_timer)
        self._paste_timer = self.after(1600, lambda: self.feedback_label.configure(text=""))

    # -------------------------------------------------------------------------
    # Display Updates & Auto-Scaling
    # -------------------------------------------------------------------------
    def _update_display(self) -> None:
        """Refreshes expression and result readouts with dynamic font scaling."""
        self.expression_label.configure(text=self.engine.previous_expression)

        text = self.engine.current_input
        # Dynamic font scaling to keep large numbers readable
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
        self.deg_rad_btn.configure(text=self.engine.angle_mode)

    # -------------------------------------------------------------------------
    # Button Handlers
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

    def _on_sqrt(self) -> None:
        """Applies square root immediately if single number, else appends sqrt(."""
        val_str = self.engine.current_input.strip()
        try:
            float(val_str)
            self.engine.apply_unary_operation("sqrt")
            self._update_display()
            if self.is_history_open:
                self._refresh_history_list()
        except ValueError:
            self._on_func("sqrt")

    def _on_exp(self) -> None:
        """Applies exponential immediately if single number, else appends exp(."""
        val_str = self.engine.current_input.strip()
        try:
            float(val_str)
            self.engine.apply_unary_operation("exp")
            self._update_display()
            if self.is_history_open:
                self._refresh_history_list()
        except ValueError:
            self._on_func("exp")

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
        """
        Binds physical keyboard keys to calculator actions:
        0-9   -> numbers
        +     -> addition
        -     -> subtraction
        *     -> multiplication
        /     -> division
        %     -> percentage
        ( )   -> parentheses
        .     -> decimal
        Enter -> calculate
        Backspace -> delete
        Escape -> clear
        Ctrl+C -> copy result
        Ctrl+V -> paste expression
        Ctrl+A -> select all
        """
        # Numbers 0-9 (Main Row & Numpad)
        for digit in "0123456789":
            self.bind_all(digit, lambda event, d=digit: self._on_number(d))
            self.bind_all(f"<KP_{digit}>", lambda event, d=digit: self._on_number(d))

        # Basic Operators
        self.bind_all("+", lambda event: self._on_operator("+"))
        self.bind_all("<KP_Add>", lambda event: self._on_operator("+"))
        self.bind_all("-", lambda event: self._on_operator("-"))
        self.bind_all("<KP_Subtract>", lambda event: self._on_operator("-"))
        self.bind_all("*", lambda event: self._on_operator("*"))
        self.bind_all("<KP_Multiply>", lambda event: self._on_operator("*"))
        self.bind_all("/", lambda event: self._on_operator("/"))
        self.bind_all("<KP_Divide>", lambda event: self._on_operator("/"))
        self.bind_all("^", lambda event: self._on_operator("^"))
        self.bind_all(".", lambda event: self._on_decimal())
        self.bind_all("<KP_Decimal>", lambda event: self._on_decimal())
        self.bind_all("%", lambda event: self._on_unary("percent"))
        self.bind_all("!", lambda event: self._on_unary("fact"))

        # Parentheses
        self.bind_all("(", lambda event: self._on_bracket("("))
        self.bind_all(")", lambda event: self._on_bracket(")"))

        # Equals / Enter
        self.bind_all("<Return>", lambda event: self._on_equals())
        self.bind_all("<KP_Enter>", lambda event: self._on_equals())
        self.bind_all("=", lambda event: self._on_equals())

        # Clear & Delete
        self.bind_all("<BackSpace>", lambda event: self._on_backspace())
        self.bind_all("<Delete>", lambda event: self._on_clear())
        self.bind_all("<Escape>", lambda event: self._on_clear())
        self.bind_all("c", lambda event: self._on_clear())
        self.bind_all("C", lambda event: self._on_clear())

        # Mathematical constants
        self.bind_all("p", lambda event: self._on_constant("pi"))
        self.bind_all("P", lambda event: self._on_constant("pi"))
        self.bind_all("e", lambda event: self._on_constant("e"))
        self.bind_all("E", lambda event: self._on_constant("e"))

        # Clipboard Shortcuts: Ctrl+C, Ctrl+V, Ctrl+A
        self.bind_all("<Control-c>", self._copy_to_clipboard)
        self.bind_all("<Control-C>", self._copy_to_clipboard)
        self.bind_all("<Control-v>", self._paste_from_clipboard)
        self.bind_all("<Control-V>", self._paste_from_clipboard)
        self.bind_all("<Control-a>", self._select_all)
        self.bind_all("<Control-A>", self._select_all)


def main():
    """Application entry point."""
    app = ScientificCalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
