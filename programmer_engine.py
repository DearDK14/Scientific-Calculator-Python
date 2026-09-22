"""
programmer_engine.py
====================
Programmer Calculator Logic Engine.

Provides:
- Multi-base integer arithmetic: Hexadecimal (HEX), Decimal (DEC), Octal (OCT), Binary (BIN)
- Word size masking and limits: QWORD (64-bit), DWORD (32-bit), WORD (16-bit), BYTE (8-bit)
- Two's complement signed and unsigned integer representation
- Bitwise operations: AND, OR, XOR, NOT, Left Shift (<<), Right Shift (>>)
- Arithmetic operations: +, -, *, /, % with divide-by-zero protection
- Individual bit flipping (0..63) for interactive bit matrix displays
- Clean string formatting per base (including nibble-spaced binary)
"""

from enum import IntEnum
from typing import Dict, List, Optional, Tuple


class NumberBase(IntEnum):
    """Supported numeral systems."""
    HEX = 16
    DEC = 10
    OCT = 8
    BIN = 2


class WordSize(IntEnum):
    """Supported word bit-widths."""
    QWORD = 64
    DWORD = 32
    WORD = 16
    BYTE = 8


# Mask and range bounds lookup per word size
WORD_CONFIG = {
    WordSize.QWORD: {
        "bits": 64,
        "mask": 0xFFFFFFFFFFFFFFFF,
        "signed_min": -0x8000000000000000,
        "signed_max": 0x7FFFFFFFFFFFFFFF,
        "name": "QWORD (64-bit)",
    },
    WordSize.DWORD: {
        "bits": 32,
        "mask": 0xFFFFFFFF,
        "signed_min": -0x80000000,
        "signed_max": 0x7FFFFFFF,
        "name": "DWORD (32-bit)",
    },
    WordSize.WORD: {
        "bits": 16,
        "mask": 0xFFFF,
        "signed_min": -0x8000,
        "signed_max": 0x7FFF,
        "name": "WORD (16-bit)",
    },
    WordSize.BYTE: {
        "bits": 8,
        "mask": 0xFF,
        "signed_min": -0x80,
        "signed_max": 0x7F,
        "name": "BYTE (8-bit)",
    },
}

VALID_CHARS_PER_BASE = {
    NumberBase.HEX: set("0123456789ABCDEFabcdef"),
    NumberBase.DEC: set("0123456789"),
    NumberBase.OCT: set("01234567"),
    NumberBase.BIN: set("01"),
}


class ProgrammerEngine:
    """
    Decoupled integer calculation and bitwise logic engine for Programmer mode.
    Maintains current internal value masked to word size, handles conversions,
    and supports step-by-step operand/operator execution.
    """

    def __init__(self, history_manager=None):
        self.history_manager = history_manager

        # Configuration
        self.active_base: NumberBase = NumberBase.DEC
        self.word_size: WordSize = WordSize.QWORD
        self.is_signed: bool = True

        # State
        self.current_value: int = 0  # Stored as unsigned integer masked to word_size
        self.stored_operand: Optional[int] = None
        self.pending_operator: Optional[str] = None
        self.previous_expression: str = ""
        self.input_buffer: str = "0"
        self.is_new_input: bool = True
        self.error_message: Optional[str] = None

    # -------------------------------------------------------------------------
    # Configuration Setters
    # -------------------------------------------------------------------------
    @property
    def mask(self) -> int:
        return WORD_CONFIG[self.word_size]["mask"]

    @property
    def bits(self) -> int:
        return WORD_CONFIG[self.word_size]["bits"]

    def set_word_size(self, size: WordSize) -> None:
        """Sets active word size (8, 16, 32, 64) and masks current values."""
        self.word_size = size
        self.current_value &= self.mask
        if self.stored_operand is not None:
            self.stored_operand &= self.mask
        self._sync_buffer_from_value()

    def set_base(self, base: NumberBase) -> None:
        """Switches the active numeral base and updates the input buffer text."""
        self.active_base = base
        self._sync_buffer_from_value()

    def set_signed(self, is_signed: bool) -> None:
        """Toggles between signed and unsigned display representation."""
        self.is_signed = is_signed
        self._sync_buffer_from_value()

    # -------------------------------------------------------------------------
    # Value Conversions & Interpretations
    # -------------------------------------------------------------------------
    def to_signed(self, unsigned_val: int) -> int:
        """Converts an unsigned integer masked to the word size into its two's complement signed value."""
        unsigned_val &= self.mask
        sign_bit = 1 << (self.bits - 1)
        if unsigned_val & sign_bit:
            return unsigned_val - (1 << self.bits)
        return unsigned_val

    def to_unsigned(self, signed_val: int) -> int:
        """Converts a signed integer into its unsigned integer bit pattern masked to word size."""
        return signed_val & self.mask

    def get_display_int(self) -> int:
        """Returns the integer value taking active signed/unsigned mode into account."""
        if self.is_signed:
            return self.to_signed(self.current_value)
        return self.current_value & self.mask

    # -------------------------------------------------------------------------
    # Input Handling
    # -------------------------------------------------------------------------
    def input_digit(self, char: str) -> bool:
        """
        Appends a character digit to the input buffer if valid for the active base.
        Returns True if accepted, False otherwise.
        """
        char = char.upper()
        if char not in VALID_CHARS_PER_BASE[self.active_base]:
            return False

        if self.error_message:
            self.clear_all()

        if self.is_new_input:
            new_buffer = char
            self.is_new_input = False
        else:
            if self.input_buffer == "0" and char != "0":
                new_buffer = char
            elif self.input_buffer == "0" and char == "0":
                return True
            else:
                new_buffer = self.input_buffer + char

        try:
            val = int(new_buffer, int(self.active_base))
            # Test if value fits in word size
            if val > self.mask:
                return False  # Overflow for this word size
            self.current_value = val & self.mask
            self.input_buffer = new_buffer
            return True
        except ValueError:
            return False

    def backspace(self) -> None:
        """Removes the last digit from the input buffer."""
        if self.error_message:
            self.clear_all()
            return

        if self.is_new_input or len(self.input_buffer) <= 1:
            self.current_value = 0
            self.input_buffer = "0"
            self.is_new_input = True
        else:
            self.input_buffer = self.input_buffer[:-1]
            try:
                self.current_value = int(self.input_buffer, int(self.active_base)) & self.mask
            except ValueError:
                self.current_value = 0
                self.input_buffer = "0"

    def clear_entry(self) -> None:
        """Clears current active input buffer to 0."""
        self.current_value = 0
        self.input_buffer = "0"
        self.is_new_input = True
        self.error_message = None

    def clear_all(self) -> None:
        """Resets all operands, pending operators, and buffers."""
        self.current_value = 0
        self.stored_operand = None
        self.pending_operator = None
        self.previous_expression = ""
        self.input_buffer = "0"
        self.is_new_input = True
        self.error_message = None

    def set_value(self, val: int) -> None:
        """Directly sets the internal integer value."""
        self.current_value = val & self.mask
        self.error_message = None
        self.is_new_input = True
        self._sync_buffer_from_value()

    def _sync_buffer_from_value(self) -> None:
        """Updates input buffer representation to reflect self.current_value in active_base."""
        val = self.current_value & self.mask
        if self.active_base == NumberBase.HEX:
            self.input_buffer = f"{val:X}"
        elif self.active_base == NumberBase.DEC:
            if self.is_signed:
                self.input_buffer = str(self.to_signed(val))
            else:
                self.input_buffer = str(val)
        elif self.active_base == NumberBase.OCT:
            self.input_buffer = f"{val:o}"
        elif self.active_base == NumberBase.BIN:
            self.input_buffer = f"{val:b}"

    # -------------------------------------------------------------------------
    # Bit Manipulation
    # -------------------------------------------------------------------------
    def toggle_bit(self, bit_index: int) -> bool:
        """
        Toggles the bit at bit_index (0 to 63).
        Only bits within the active word size can be toggled.
        Returns True if toggled, False if out of range.
        """
        if not (0 <= bit_index < self.bits):
            return False

        self.current_value ^= (1 << bit_index)
        self.current_value &= self.mask
        self.is_new_input = False
        self._sync_buffer_from_value()
        return True

    def set_bit(self, bit_index: int, bit_value: int) -> bool:
        """Sets or clears the bit at bit_index."""
        if not (0 <= bit_index < self.bits):
            return False

        if bit_value:
            self.current_value |= (1 << bit_index)
        else:
            self.current_value &= ~(1 << bit_index)
        self.current_value &= self.mask
        self.is_new_input = False
        self._sync_buffer_from_value()
        return True

    def get_bit(self, bit_index: int) -> int:
        """Returns 0 or 1 for the bit at bit_index."""
        if not (0 <= bit_index < 64):
            return 0
        return (self.current_value >> bit_index) & 1

    def get_bits_list(self) -> List[int]:
        """Returns a 64-element list of bits from bit 63 down to bit 0."""
        return [(self.current_value >> i) & 1 for i in range(63, -1, -1)]

    # -------------------------------------------------------------------------
    # Unary Operations
    # -------------------------------------------------------------------------
    def apply_unary_operation(self, op: str) -> Tuple[bool, Optional[str]]:
        """
        Applies a unary operation to current_value:
        - 'NOT': bitwise invert
        - 'NEG' / '±': two's complement negate
        """
        if self.error_message:
            return False, self.error_message

        op = op.upper()
        if op == "NOT":
            self.current_value = (~self.current_value) & self.mask
            self.is_new_input = True
            self._sync_buffer_from_value()
            return True, None

        elif op in ("NEG", "±"):
            # Two's complement negate
            self.current_value = (-self.current_value) & self.mask
            self.is_new_input = True
            self._sync_buffer_from_value()
            return True, None

        return False, f"Unknown unary operation: {op}"

    # -------------------------------------------------------------------------
    # Binary Operations & Calculation
    # -------------------------------------------------------------------------
    def set_binary_operator(self, op: str) -> Tuple[bool, Optional[str]]:
        """
        Sets a pending binary operator. If an operator was already pending
        and the user entered a new number, evaluates the previous operation first.
        Supported operators: '+', '-', '*', '/', '%', 'AND', 'OR', 'XOR', 'LSH', 'RSH'
        """
        if self.error_message:
            self.clear_all()

        op_norm = self._normalize_operator(op)

        # If chaining operations (e.g. 5 + 3 * ...)
        if self.pending_operator is not None and not self.is_new_input:
            success, err = self.calculate()
            if not success:
                return False, err

        self.stored_operand = self.current_value & self.mask
        self.pending_operator = op_norm
        self.is_new_input = True

        # Update expression preview
        base_str = self._format_operand_for_preview(self.stored_operand)
        self.previous_expression = f"{base_str} {op_norm}"
        return True, None

    def calculate(self) -> Tuple[bool, Optional[str]]:
        """
        Executes the pending binary calculation with stored_operand and current_value.
        Returns (success: bool, error_message: Optional[str]).
        """
        if self.pending_operator is None or self.stored_operand is None:
            return True, None

        a = self.stored_operand & self.mask
        b = self.current_value & self.mask
        op = self.pending_operator

        res: int = 0
        try:
            op_check = op.upper()
            if op == "+":
                res = (a + b) & self.mask
            elif op == "-":
                res = (a - b) & self.mask
            elif op == "*":
                res = (a * b) & self.mask
            elif op in ("/", "÷"):
                if b == 0:
                    self.error_message = "Cannot divide by zero"
                    return False, self.error_message
                res = (a // b) & self.mask
            elif op in ("%", "MOD"):
                if b == 0:
                    self.error_message = "Cannot divide by zero"
                    return False, self.error_message
                res = (a % b) & self.mask
            elif op_check == "AND":
                res = (a & b) & self.mask
            elif op_check == "OR":
                res = (a | b) & self.mask
            elif op_check == "XOR":
                res = (a ^ b) & self.mask
            elif op_check in ("LSH", "<<"):
                # Clamp shift count to word bit width
                shift_count = b % self.bits if b >= 0 else 0
                res = (a << shift_count) & self.mask
            elif op_check in ("RSH", ">>"):
                shift_count = b % self.bits if b >= 0 else 0
                if self.is_signed:
                    # Arithmetic right shift: convert to signed, shift, then mask
                    signed_a = self.to_signed(a)
                    res = (signed_a >> shift_count) & self.mask
                else:
                    # Logical right shift
                    res = (a >> shift_count) & self.mask
            else:
                return False, f"Unknown operator: {op}"

        except Exception as ex:
            self.error_message = str(ex)
            return False, self.error_message

        # Record expression for history
        expr_a = self._format_operand_for_preview(a)
        expr_b = self._format_operand_for_preview(b)
        full_expr = f"{expr_a} {op} {expr_b}"
        self.previous_expression = f"{full_expr} ="

        self.current_value = res & self.mask
        self.stored_operand = None
        self.pending_operator = None
        self.is_new_input = True
        self._sync_buffer_from_value()

        # Record to history manager if present
        if self.history_manager is not None:
            res_str = self._format_operand_for_preview(self.current_value)
            self.history_manager.add(full_expr, res_str)

        return True, None

    def _normalize_operator(self, op: str) -> str:
        op = op.strip().upper()
        if op in ("+", "ADD"):
            return "+"
        elif op in ("-", "SUB"):
            return "-"
        elif op in ("*", "×", "MUL"):
            return "*"
        elif op in ("/", "÷", "DIV"):
            return "/"
        elif op in ("%", "MOD"):
            return "%"
        elif op in ("<<", "LSH"):
            return "Lsh"
        elif op in (">>", "RSH"):
            return "Rsh"
        elif op in ("AND", "&"):
            return "AND"
        elif op in ("OR", "|"):
            return "OR"
        elif op in ("XOR", "^"):
            return "XOR"
        return op

    def _format_operand_for_preview(self, val: int) -> str:
        val &= self.mask
        if self.active_base == NumberBase.HEX:
            return f"0x{val:X}"
        elif self.active_base == NumberBase.OCT:
            return f"0o{val:o}"
        elif self.active_base == NumberBase.BIN:
            return f"0b{val:b}"
        else:
            if self.is_signed:
                return str(self.to_signed(val))
            return str(val)

    # -------------------------------------------------------------------------
    # Formatted Base Representations for Readouts
    # -------------------------------------------------------------------------
    def get_hex_string(self) -> str:
        """Returns uppercase Hex string formatted cleanly."""
        val = self.current_value & self.mask
        return f"{val:X}"

    def get_dec_string(self) -> str:
        """Returns Decimal string (signed or unsigned according to active mode)."""
        val = self.current_value & self.mask
        if self.is_signed:
            return str(self.to_signed(val))
        return str(val)

    def get_oct_string(self) -> str:
        """Returns Octal string."""
        val = self.current_value & self.mask
        return f"{val:o}"

    def get_bin_string(self, group_nibbles: bool = True) -> str:
        """
        Returns binary representation padded to active word bit width,
        optionally formatted in groups of 4 bits (nibbles).
        """
        val = self.current_value & self.mask
        raw_bin = f"{val:0{self.bits}b}"
        if not group_nibbles:
            return raw_bin

        # Group in 4s from right
        chunks = [raw_bin[i:i+4] for i in range(0, len(raw_bin), 4)]
        return " ".join(chunks)

    def get_all_base_readouts(self) -> Dict[str, str]:
        """Returns dictionary of current value in all 4 numeral systems."""
        return {
            "HEX": self.get_hex_string(),
            "DEC": self.get_dec_string(),
            "OCT": self.get_oct_string(),
            "BIN": self.get_bin_string(group_nibbles=True),
        }
