"""
views/programmer_view.py
========================
Programmer Calculator Mode View.

Features:
- Multi-base integer display: HEX, DEC, OCT, BIN (interactive clickable rows)
- Real-time base conversions and dynamic keypad digit filtering
- Word size selection: QWORD (64-bit), DWORD (32-bit), WORD (16-bit), BYTE (8-bit)
- Two's complement signed and unsigned integer representation
- Interactive 64-bit matrix arranged in 4-bit nibbles with direct bit flipping
- Bitwise logic: AND, OR, XOR, NOT, Left Shift (Lsh), Right Shift (Rsh)
- Binary arithmetic: +, -, *, /, % with divide-by-zero protection
- Full keyboard routing and history integration
"""

from typing import Any, Dict, List, Optional
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip
from programmer_engine import NumberBase, ProgrammerEngine, WordSize


class ProgrammerView(BaseModeView):
    """
    Complete Programmer Calculator mode view.
    """

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, app, **kwargs)
        self.engine = ProgrammerEngine(history_manager=self.app.history_mgr)

        # UI references
        self.base_rows: Dict[NumberBase, Dict[str, Any]] = {}
        self.bit_buttons: List[ctk.CTkButton] = []  # 64 buttons (bit 63 down to 0)
        self.keypad_buttons: Dict[str, ctk.CTkButton] = {}

        self._copied_timer = None
        self._build_ui()
        self._update_display()

    # -------------------------------------------------------------------------
    # BaseModeView Interface
    # -------------------------------------------------------------------------
    def get_title(self) -> str:
        return "Programmer"

    def get_mode_id(self) -> str:
        return "programmer"

    def handles_keyboard(self) -> bool:
        return True

    def on_activate(self) -> None:
        self._update_display()

    def handle_key_action(self, action_type: str, value: Optional[str] = None) -> None:
        """Processes global physical keyboard input."""
        if action_type == "number" and value:
            self._on_digit(value)
        elif action_type == "operator" and value:
            self._on_operator(value)
        elif action_type == "equals":
            self._on_equals()
        elif action_type == "backspace":
            self._on_backspace()
        elif action_type in ("clear", "all_clear"):
            self._on_clear()
        elif action_type == "copy":
            self._copy_current_value()
        elif action_type == "paste":
            self._paste_from_clipboard()

    # -------------------------------------------------------------------------
    # UI Layout Construction
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top Base Readouts Card
        self.grid_rowconfigure(1, weight=0)  # Word Size & Representation Bar
        self.grid_rowconfigure(2, weight=0)  # 64-bit Matrix Card
        self.grid_rowconfigure(3, weight=1)  # Keypad Card

        self._build_base_readouts(self)
        self._build_controls_bar(self)
        self._build_bit_matrix(self)
        self._build_keypad(self)

    # 1. Base Readouts Card
    def _build_base_readouts(self, parent: ctk.CTkFrame) -> None:
        self.readout_card = ctk.CTkFrame(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        self.readout_card.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 6))
        self.readout_card.grid_columnconfigure(1, weight=1)

        # Header Row: Expression & Copy Button
        header_frame = ctk.CTkFrame(self.readout_card, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 2))
        header_frame.grid_columnconfigure(0, weight=1)

        self.expr_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=Fonts.display_formula(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="e",
        )
        self.expr_label.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.copy_btn = ctk.CTkButton(
            header_frame,
            text="📋 Copy",
            width=68,
            height=26,
            command=self._copy_current_value,
            font=Fonts.label_badge(),
            **Theme.BTN_COPY,
        )
        self.copy_btn.grid(row=0, column=1)
        CTkToolTip(self.copy_btn, "Copy active base value to clipboard (Ctrl+C)")

        # 4 Base Rows: HEX, DEC, OCT, BIN
        bases = [
            (NumberBase.HEX, "HEX"),
            (NumberBase.DEC, "DEC"),
            (NumberBase.OCT, "OCT"),
            (NumberBase.BIN, "BIN"),
        ]

        for idx, (base_enum, base_name) in enumerate(bases):
            row_frame = ctk.CTkFrame(
                self.readout_card,
                fg_color="transparent",
                corner_radius=6,
                height=30,
            )
            row_frame.grid(row=idx + 1, column=0, columnspan=2, sticky="ew", padx=8, pady=2)
            row_frame.grid_columnconfigure(1, weight=1)

            # Click handler to select active base
            def make_selector(b=base_enum):
                return lambda e=None: self._on_select_base(b)

            row_frame.bind("<Button-1>", make_selector())

            # Base name badge
            name_lbl = ctk.CTkLabel(
                row_frame,
                text=base_name,
                width=42,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            name_lbl.grid(row=0, column=0, padx=(8, 8))
            name_lbl.bind("<Button-1>", make_selector())

            # Value label
            val_lbl = ctk.CTkLabel(
                row_frame,
                text="0",
                font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
                text_color=Theme.TEXT_PRIMARY,
                anchor="e",
            )
            val_lbl.grid(row=0, column=1, sticky="ew", padx=(0, 8))
            val_lbl.bind("<Button-1>", make_selector())

            self.base_rows[base_enum] = {
                "frame": row_frame,
                "name_lbl": name_lbl,
                "val_lbl": val_lbl,
            }

    # 2. Controls Bar (Word Size & Representation)
    def _build_controls_bar(self, parent: ctk.CTkFrame) -> None:
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_columnconfigure(1, weight=0)

        # Word size segmented button
        self.word_size_seg = ctk.CTkSegmentedButton(
            bar,
            values=["QWORD (64)", "DWORD (32)", "WORD (16)", "BYTE (8)"],
            command=self._on_word_size_changed,
            font=Fonts.label_badge(),
            selected_color=Theme.ACCENT_PRIMARY,
            selected_hover_color=Theme.ACCENT_HOVER,
        )
        self.word_size_seg.set("QWORD (64)")
        self.word_size_seg.grid(row=0, column=0, sticky="w")
        CTkToolTip(self.word_size_seg, "Select bit-width capacity")

        # Signed / Unsigned segmented button
        self.signed_seg = ctk.CTkSegmentedButton(
            bar,
            values=["Signed", "Unsigned"],
            command=self._on_signed_changed,
            font=Fonts.label_badge(),
            selected_color=Theme.ACCENT_PRIMARY,
            selected_hover_color=Theme.ACCENT_HOVER,
        )
        self.signed_seg.set("Signed")
        self.signed_seg.grid(row=0, column=1, sticky="e", padx=(8, 0))
        CTkToolTip(self.signed_seg, "Toggle Two's Complement signed vs unsigned representation")

    # 3. Interactive 64-Bit Matrix Display
    def _build_bit_matrix(self, parent: ctk.CTkFrame) -> None:
        matrix_card = ctk.CTkFrame(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=10,
        )
        matrix_card.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 6))
        matrix_card.grid_columnconfigure(0, weight=1)

        # 4 rows of 16 bits = 64 bits total
        # Row 0: Bits 63..48
        # Row 1: Bits 47..32
        # Row 2: Bits 31..16
        # Row 3: Bits 15..0
        self.bit_buttons = [None] * 64

        row_defs = [
            (63, 48),
            (47, 32),
            (31, 16),
            (15, 0),
        ]

        for row_idx, (start_bit, end_bit) in enumerate(row_defs):
            row_frame = ctk.CTkFrame(matrix_card, fg_color="transparent")
            row_frame.pack(fill="x", padx=6, pady=1)

            # Left index label
            left_lbl = ctk.CTkLabel(
                row_frame,
                text=str(start_bit),
                width=24,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            left_lbl.pack(side="left")

            # Nibbles frame
            nibbles_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            nibbles_frame.pack(side="left", expand=True, fill="x")

            # 4 nibbles of 4 bits
            for nibble in range(4):
                n_frame = ctk.CTkFrame(nibbles_frame, fg_color="transparent")
                n_frame.pack(side="left", expand=True, fill="x", padx=4)

                for b_in_nibble in range(4):
                    bit_index = start_bit - (nibble * 4 + b_in_nibble)

                    def make_toggler(idx=bit_index):
                        return lambda: self._on_toggle_bit(idx)

                    bit_btn = ctk.CTkButton(
                        n_frame,
                        text="0",
                        width=18,
                        height=20,
                        command=make_toggler(),
                        font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                        fg_color="transparent",
                        hover_color=Theme.SIDEBAR_HOVER,
                        text_color=Theme.TEXT_SECONDARY,
                        corner_radius=3,
                    )
                    bit_btn.pack(side="left", expand=True, fill="x", padx=1)
                    self.bit_buttons[bit_index] = bit_btn

            # Right index label
            right_lbl = ctk.CTkLabel(
                row_frame,
                text=str(end_bit),
                width=20,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=Theme.TEXT_SECONDARY,
                anchor="e",
            )
            right_lbl.pack(side="right")

    # 4. Programmer Keypad
    def _build_keypad(self, parent: ctk.CTkFrame) -> None:
        keypad = ctk.CTkFrame(parent, fg_color="transparent")
        keypad.grid(row=3, column=0, sticky="nsew", padx=4, pady=(0, 2))

        # 6 columns x 5 rows
        for col in range(6):
            keypad.grid_columnconfigure(col, weight=1)
        for row in range(5):
            keypad.grid_rowconfigure(row, weight=1)

        # Layout grid definitions:
        # Row 0: [Lsh] [Rsh] [AND] [OR]  [XOR] [NOT]
        # Row 1: [A]   [B]   [7]   [8]   [9]   [÷]
        # Row 2: [C]   [D]   [4]   [5]   [6]   [×]
        # Row 3: [E]   [F]   [1]   [2]   [3]   [−]
        # Row 4: [CE]  [C]   [DEL] [0]   [±]   [+]  (with = or % handled smoothly)
        # Note: Let's make an intuitive 6-column keypad:
        # Col 0: Bitwise / Hex (A, C, E, Lsh)
        # Col 1: Bitwise / Hex (B, D, F, Rsh)
        # Col 2: Numbers (7, 4, 1, 0)
        # Col 3: Numbers (8, 5, 2, ±)
        # Col 4: Numbers (9, 6, 3, %)
        # Col 5: Ops (÷, ×, −, +, =)

        buttons = [
            # Row 0: Bitwise operations & Clear
            ("Lsh", 0, 0, self._on_lsh, Theme.BTN_OPERATOR),
            ("Rsh", 0, 1, self._on_rsh, Theme.BTN_OPERATOR),
            ("AND", 0, 2, lambda: self._on_operator("AND"), Theme.BTN_OPERATOR),
            ("OR", 0, 3, lambda: self._on_operator("OR"), Theme.BTN_OPERATOR),
            ("XOR", 0, 4, lambda: self._on_operator("XOR"), Theme.BTN_OPERATOR),
            ("NOT", 0, 5, self._on_not, Theme.BTN_OPERATOR),

            # Row 1: Hex A, B, 7, 8, 9, ÷
            ("A", 1, 0, lambda: self._on_digit("A"), Theme.BTN_BRACKET),
            ("B", 1, 1, lambda: self._on_digit("B"), Theme.BTN_BRACKET),
            ("7", 1, 2, lambda: self._on_digit("7"), Theme.BTN_NUMBER),
            ("8", 1, 3, lambda: self._on_digit("8"), Theme.BTN_NUMBER),
            ("9", 1, 4, lambda: self._on_digit("9"), Theme.BTN_NUMBER),
            ("÷", 1, 5, lambda: self._on_operator("÷"), Theme.BTN_OPERATOR),

            # Row 2: Hex C, D, 4, 5, 6, ×
            ("C_hex", 2, 0, lambda: self._on_digit("C"), Theme.BTN_BRACKET),
            ("D", 2, 1, lambda: self._on_digit("D"), Theme.BTN_BRACKET),
            ("4", 2, 2, lambda: self._on_digit("4"), Theme.BTN_NUMBER),
            ("5", 2, 3, lambda: self._on_digit("5"), Theme.BTN_NUMBER),
            ("6", 2, 4, lambda: self._on_digit("6"), Theme.BTN_NUMBER),
            ("×", 2, 5, lambda: self._on_operator("×"), Theme.BTN_OPERATOR),

            # Row 3: Hex E, F, 1, 2, 3, −
            ("E", 3, 0, lambda: self._on_digit("E"), Theme.BTN_BRACKET),
            ("F", 3, 1, lambda: self._on_digit("F"), Theme.BTN_BRACKET),
            ("1", 3, 2, lambda: self._on_digit("1"), Theme.BTN_NUMBER),
            ("2", 3, 3, lambda: self._on_digit("2"), Theme.BTN_NUMBER),
            ("3", 3, 4, lambda: self._on_digit("3"), Theme.BTN_NUMBER),
            ("−", 3, 5, lambda: self._on_operator("-"), Theme.BTN_OPERATOR),

            # Row 4: Clear actions, 0, ±, %, +, =
            # We have 6 columns. Let's place: [CE] [DEL] [0] [±] [%] [=]
            ("CE", 4, 0, self._on_clear_entry, Theme.BTN_ACTION),
            ("DEL", 4, 1, self._on_backspace, Theme.BTN_ACTION),
            ("0", 4, 2, lambda: self._on_digit("0"), Theme.BTN_NUMBER),
            ("±", 4, 3, self._on_negate, Theme.BTN_NUMBER),
            ("+", 4, 4, lambda: self._on_operator("+"), Theme.BTN_OPERATOR),
            ("=", 4, 5, self._on_equals, Theme.BTN_EQUALS),
        ]

        for key_id, r, c, cmd, style in buttons:
            label = "C" if key_id == "C_hex" else key_id
            btn = ctk.CTkButton(
                keypad,
                text=label,
                command=cmd,
                font=Fonts.button_standard(),
                **style,
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            self.keypad_buttons[key_id] = btn

    # -------------------------------------------------------------------------
    # Display Synchronization
    # -------------------------------------------------------------------------
    def _update_display(self) -> None:
        """Synchronizes base readouts, active highlight, bit matrix, and button states."""
        # 1. Expression preview
        self.expr_label.configure(text=self.engine.previous_expression)

        # 2. 4 Base readouts
        readouts = self.engine.get_all_base_readouts()
        for base_enum, comps in self.base_rows.items():
            base_key = base_enum.name
            val_text = readouts.get(base_key, "0")
            comps["val_lbl"].configure(text=val_text)

            is_active = (base_enum == self.engine.active_base)
            if is_active:
                comps["frame"].configure(fg_color=Theme.SIDEBAR_HOVER)
                comps["name_lbl"].configure(text_color=Theme.TEXT_ACCENT)
                comps["val_lbl"].configure(text_color=Theme.TEXT_ACCENT)
            else:
                comps["frame"].configure(fg_color="transparent")
                comps["name_lbl"].configure(text_color=Theme.TEXT_SECONDARY)
                comps["val_lbl"].configure(text_color=Theme.TEXT_PRIMARY)

        # 3. Bit Matrix (64 bits)
        active_bits = self.engine.bits
        for bit_idx in range(64):
            btn = self.bit_buttons[bit_idx]
            if btn is None:
                continue

            if bit_idx < active_bits:
                # Within active word size
                bit_val = self.engine.get_bit(bit_idx)
                btn.configure(
                    text=str(bit_val),
                    state="normal",
                    text_color=Theme.TEXT_ACCENT if bit_val == 1 else Theme.TEXT_PRIMARY,
                )
            else:
                # Outside word size: dimmed/disabled
                btn.configure(
                    text="·",
                    state="disabled",
                    text_color=Theme.TEXT_MUTED,
                )

        # 4. Keypad digit enabling based on active base
        self._filter_keypad_buttons()

    def _filter_keypad_buttons(self) -> None:
        """Enables or disables keypad buttons based on the active numeral base."""
        base = self.engine.active_base
        hex_buttons = ["A", "B", "C_hex", "D", "E", "F"]
        oct_buttons = ["8", "9"]
        bin_buttons = ["2", "3", "4", "5", "6", "7"]

        # Hex buttons (A-F)
        for hb in hex_buttons:
            btn = self.keypad_buttons.get(hb)
            if btn:
                state = "normal" if base == NumberBase.HEX else "disabled"
                btn.configure(state=state)

        # Digits 8-9
        for ob in oct_buttons:
            btn = self.keypad_buttons.get(ob)
            if btn:
                state = "normal" if base in (NumberBase.HEX, NumberBase.DEC) else "disabled"
                btn.configure(state=state)

        # Digits 2-7
        for bb in bin_buttons:
            btn = self.keypad_buttons.get(bb)
            if btn:
                state = "normal" if base in (NumberBase.HEX, NumberBase.DEC, NumberBase.OCT) else "disabled"
                btn.configure(state=state)

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------
    def _on_select_base(self, base: NumberBase) -> None:
        self.engine.set_base(base)
        self._update_display()

    def _on_word_size_changed(self, choice: str) -> None:
        if "64" in choice:
            self.engine.set_word_size(WordSize.QWORD)
        elif "32" in choice:
            self.engine.set_word_size(WordSize.DWORD)
        elif "16" in choice:
            self.engine.set_word_size(WordSize.WORD)
        elif "8" in choice:
            self.engine.set_word_size(WordSize.BYTE)
        self._update_display()

    def _on_signed_changed(self, choice: str) -> None:
        is_signed = (choice == "Signed")
        self.engine.set_signed(is_signed)
        self._update_display()

    def _on_toggle_bit(self, bit_index: int) -> None:
        self.engine.toggle_bit(bit_index)
        self._update_display()

    def _on_digit(self, char: str) -> None:
        if self.engine.input_digit(char):
            self._update_display()

    def _on_operator(self, op: str) -> None:
        success, err = self.engine.set_binary_operator(op)
        if not success and err:
            self._show_feedback(err, Theme.TEXT_ERROR)
        self._update_display()

    def _on_lsh(self) -> None:
        self._on_operator("Lsh")

    def _on_rsh(self) -> None:
        self._on_operator("Rsh")

    def _on_not(self) -> None:
        success, err = self.engine.apply_unary_operation("NOT")
        if not success and err:
            self._show_feedback(err, Theme.TEXT_ERROR)
        self._update_display()

    def _on_negate(self) -> None:
        success, err = self.engine.apply_unary_operation("NEG")
        if not success and err:
            self._show_feedback(err, Theme.TEXT_ERROR)
        self._update_display()

    def _on_equals(self) -> None:
        success, err = self.engine.calculate()
        if not success and err:
            self._show_feedback(err, Theme.TEXT_ERROR)
        self._update_display()

    def _on_backspace(self) -> None:
        self.engine.backspace()
        self._update_display()

    def _on_clear_entry(self) -> None:
        self.engine.clear_entry()
        self._update_display()

    def _on_clear(self) -> None:
        self.engine.clear_all()
        self._update_display()

    # -------------------------------------------------------------------------
    # History Integration & Clipboard
    # -------------------------------------------------------------------------
    def load_history_value(self, result_str: str, expr_str: str = "") -> None:
        """Loads a previous calculation result into the programmer engine."""
        try:
            # Strip prefixes like 0x, 0b, 0o if present
            clean = result_str.strip()
            if clean.startswith("0x") or clean.startswith("0X"):
                val = int(clean, 16)
            elif clean.startswith("0b") or clean.startswith("0B"):
                val = int(clean, 2)
            elif clean.startswith("0o") or clean.startswith("0O"):
                val = int(clean, 8)
            else:
                val = int(clean)
            self.engine.set_value(val)
            self._update_display()
            self._show_feedback("Loaded from history", Theme.TEXT_ACCENT)
        except ValueError:
            pass

    def _copy_current_value(self) -> None:
        val_str = self.engine.input_buffer
        self.app.clipboard_clear()
        self.app.clipboard_append(val_str)
        self._show_feedback("Copied!", Theme.TEXT_ACCENT)

    def _paste_from_clipboard(self) -> None:
        try:
            pasted = self.app.clipboard_get().strip()
            # Try to input digits from paste
            for ch in pasted:
                self.engine.input_digit(ch)
            self._update_display()
            self._show_feedback("Pasted!", Theme.TEXT_ACCENT)
        except Exception:
            pass

    def _show_feedback(self, msg: str, color: str) -> None:
        orig = self.copy_btn.cget("text")
        self.copy_btn.configure(text=msg, text_color=color)

        if self._copied_timer:
            self.after_cancel(self._copied_timer)

        def restore():
            self.copy_btn.configure(text=orig, text_color=Theme.BTN_COPY["text_color"])

        self._copied_timer = self.after(1400, restore)
