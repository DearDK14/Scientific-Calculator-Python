"""
test_programmer.py
==================
Unit tests for Programmer Calculator Engine (programmer_engine.py).
Validates multi-base conversions, word sizes, two's complement signed/unsigned logic,
bitwise logic, shifts, arithmetic, division by zero, and bit flipping.
"""

import unittest
from programmer_engine import NumberBase, ProgrammerEngine, WordSize
from history import HistoryManager


class TestProgrammerEngine(unittest.TestCase):
    """Exhaustive test suite for ProgrammerEngine."""

    def setUp(self):
        self.engine = ProgrammerEngine()

    # -------------------------------------------------------------------------
    # 1. Base Conversions & Digit Input Validation
    # -------------------------------------------------------------------------
    def test_digit_input_per_base(self):
        # In DEC: 0-9 allowed, A-F rejected
        self.engine.set_base(NumberBase.DEC)
        self.assertTrue(self.engine.input_digit("1"))
        self.assertTrue(self.engine.input_digit("5"))
        self.assertFalse(self.engine.input_digit("A"))
        self.assertFalse(self.engine.input_digit("F"))
        self.assertEqual(self.engine.current_value, 15)

        # In HEX: 0-9 and A-F allowed
        self.engine.set_base(NumberBase.HEX)
        self.engine.clear_all()
        self.assertTrue(self.engine.input_digit("A"))
        self.assertTrue(self.engine.input_digit("F"))
        self.assertEqual(self.engine.current_value, 0xAF)
        self.assertEqual(self.engine.get_hex_string(), "AF")
        self.assertEqual(self.engine.get_dec_string(), "175")

        # In OCT: 0-7 allowed, 8 and 9 rejected
        self.engine.set_base(NumberBase.OCT)
        self.engine.clear_all()
        self.assertTrue(self.engine.input_digit("7"))
        self.assertFalse(self.engine.input_digit("8"))
        self.assertFalse(self.engine.input_digit("9"))
        self.assertEqual(self.engine.current_value, 7)

        # In BIN: only 0 and 1 allowed
        self.engine.set_base(NumberBase.BIN)
        self.engine.clear_all()
        self.assertTrue(self.engine.input_digit("1"))
        self.assertTrue(self.engine.input_digit("0"))
        self.assertTrue(self.engine.input_digit("1"))
        self.assertFalse(self.engine.input_digit("2"))
        self.assertEqual(self.engine.current_value, 0b101)
        self.assertEqual(self.engine.get_dec_string(), "5")

    def test_all_base_readouts(self):
        self.engine.set_value(0x1F)  # 31 decimal
        readouts = self.engine.get_all_base_readouts()
        self.assertEqual(readouts["HEX"], "1F")
        self.assertEqual(readouts["DEC"], "31")
        self.assertEqual(readouts["OCT"], "37")
        self.assertTrue(readouts["BIN"].endswith("0001 1111"))

    # -------------------------------------------------------------------------
    # 2. Word Sizes & Truncation
    # -------------------------------------------------------------------------
    def test_word_size_masking(self):
        self.engine.set_value(0x123456789ABCDEF)
        self.assertEqual(self.engine.word_size, WordSize.QWORD)

        # Truncate to DWORD (32-bit)
        self.engine.set_word_size(WordSize.DWORD)
        self.assertEqual(self.engine.current_value, 0x89ABCDEF)

        # Truncate to WORD (16-bit)
        self.engine.set_word_size(WordSize.WORD)
        self.assertEqual(self.engine.current_value, 0xCDEF)

        # Truncate to BYTE (8-bit)
        self.engine.set_word_size(WordSize.BYTE)
        self.assertEqual(self.engine.current_value, 0xEF)

    # -------------------------------------------------------------------------
    # 3. Two's Complement Signed / Unsigned Representation
    # -------------------------------------------------------------------------
    def test_signed_and_unsigned_interpretation(self):
        self.engine.set_word_size(WordSize.BYTE)

        # 0xFF in 8-bit
        self.engine.set_value(0xFF)
        self.engine.set_signed(True)
        self.assertEqual(self.engine.get_display_int(), -1)
        self.assertEqual(self.engine.get_dec_string(), "-1")

        self.engine.set_signed(False)
        self.assertEqual(self.engine.get_display_int(), 255)
        self.assertEqual(self.engine.get_dec_string(), "255")

        # 0x80 in 8-bit (-128 signed, 128 unsigned)
        self.engine.set_value(0x80)
        self.engine.set_signed(True)
        self.assertEqual(self.engine.get_display_int(), -128)
        self.engine.set_signed(False)
        self.assertEqual(self.engine.get_display_int(), 128)

        # 0x7F in 8-bit (127 in both)
        self.engine.set_value(0x7F)
        self.engine.set_signed(True)
        self.assertEqual(self.engine.get_display_int(), 127)
        self.engine.set_signed(False)
        self.assertEqual(self.engine.get_display_int(), 127)

    # -------------------------------------------------------------------------
    # 4. Bitwise Operations (AND, OR, XOR, NOT, Negate)
    # -------------------------------------------------------------------------
    def test_bitwise_operations(self):
        self.engine.set_word_size(WordSize.BYTE)

        # AND
        self.engine.set_value(0b11001100)
        self.engine.set_binary_operator("AND")
        self.engine.set_value(0b10101010)
        success, _ = self.engine.calculate()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0b10001000)

        # OR
        self.engine.set_value(0b11000000)
        self.engine.set_binary_operator("OR")
        self.engine.set_value(0b00001111)
        success, _ = self.engine.calculate()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0b11001111)

        # XOR
        self.engine.set_value(0b11110000)
        self.engine.set_binary_operator("XOR")
        self.engine.set_value(0b10101010)
        success, _ = self.engine.calculate()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0b01011010)

        # NOT (in 8-bit: ~0x0F = 0xF0)
        self.engine.set_value(0x0F)
        success, _ = self.engine.apply_unary_operation("NOT")
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0xF0)

        # Negate (± in 8-bit: -1 is 0xFF)
        self.engine.set_value(1)
        success, _ = self.engine.apply_unary_operation("NEG")
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0xFF)

    # -------------------------------------------------------------------------
    # 5. Bit Shifts (Lsh, Rsh)
    # -------------------------------------------------------------------------
    def test_shift_operations(self):
        self.engine.set_word_size(WordSize.BYTE)

        # Left shift: 0b00000101 << 2 = 0b00010100 (20)
        self.engine.set_value(5)
        self.engine.set_binary_operator("Lsh")
        self.engine.set_value(2)
        success, _ = self.engine.calculate()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 20)

        # Logical Right shift (unsigned): 0b10000000 >> 2 = 0b00100000
        self.engine.set_signed(False)
        self.engine.set_value(0x80)
        self.engine.set_binary_operator("Rsh")
        self.engine.set_value(2)
        success, _ = self.engine.calculate()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0x20)

        # Arithmetic Right shift (signed): -128 (0x80) >> 2 = -32 (0xE0)
        self.engine.set_signed(True)
        self.engine.set_value(0x80)
        self.engine.set_binary_operator("Rsh")
        self.engine.set_value(2)
        success, _ = self.engine.calculate()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_value, 0xE0)
        self.assertEqual(self.engine.to_signed(self.engine.current_value), -32)

    # -------------------------------------------------------------------------
    # 6. Binary Arithmetic (+, -, *, /, %) & Divide by Zero
    # -------------------------------------------------------------------------
    def test_arithmetic_operations(self):
        self.engine.set_word_size(WordSize.WORD)  # 16-bit

        # Addition with overflow wrapping
        self.engine.set_value(0xFFFF)
        self.engine.set_binary_operator("+")
        self.engine.set_value(1)
        self.engine.calculate()
        self.assertEqual(self.engine.current_value, 0)  # Wrapped to 0

        # Subtraction
        self.engine.set_value(100)
        self.engine.set_binary_operator("-")
        self.engine.set_value(25)
        self.engine.calculate()
        self.assertEqual(self.engine.current_value, 75)

        # Multiplication
        self.engine.set_value(12)
        self.engine.set_binary_operator("*")
        self.engine.set_value(12)
        self.engine.calculate()
        self.assertEqual(self.engine.current_value, 144)

        # Integer Division
        self.engine.set_value(100)
        self.engine.set_binary_operator("/")
        self.engine.set_value(7)
        self.engine.calculate()
        self.assertEqual(self.engine.current_value, 14)

        # Modulo
        self.engine.set_value(100)
        self.engine.set_binary_operator("%")
        self.engine.set_value(7)
        self.engine.calculate()
        self.assertEqual(self.engine.current_value, 2)

    def test_division_by_zero_and_recovery(self):
        self.engine.set_value(50)
        self.engine.set_binary_operator("/")
        self.engine.set_value(0)
        success, err = self.engine.calculate()
        self.assertFalse(success)
        self.assertEqual(err, "Cannot divide by zero")

        # Subsequent input clears error and accepts new value
        self.engine.input_digit("9")
        self.assertEqual(self.engine.current_value, 9)
        self.assertIsNone(self.engine.error_message)

    # -------------------------------------------------------------------------
    # 7. Bit Matrix Manipulation
    # -------------------------------------------------------------------------
    def test_bit_toggling_and_bounds(self):
        self.engine.set_word_size(WordSize.BYTE)  # 8 bits: 0..7
        self.engine.set_value(0)

        # Toggle bit 0 -> 1
        self.assertTrue(self.engine.toggle_bit(0))
        self.assertEqual(self.engine.current_value, 1)

        # Toggle bit 3 -> 1 + 8 = 9
        self.assertTrue(self.engine.toggle_bit(3))
        self.assertEqual(self.engine.current_value, 9)

        # Toggle bit 0 back -> 8
        self.assertTrue(self.engine.toggle_bit(0))
        self.assertEqual(self.engine.current_value, 8)

        # Out-of-bounds bit for BYTE (e.g. bit 10) rejected
        self.assertFalse(self.engine.toggle_bit(10))
        self.assertEqual(self.engine.current_value, 8)

    # -------------------------------------------------------------------------
    # 8. History Integration
    # -------------------------------------------------------------------------
    def test_history_logging(self):
        history = HistoryManager(storage_file=None, max_entries=10)
        history.clear()
        prog_engine = ProgrammerEngine(history_manager=history)

        prog_engine.set_value(10)
        prog_engine.set_binary_operator("+")
        prog_engine.set_value(20)
        prog_engine.calculate()

        entries = history.get_all()
        self.assertEqual(len(entries), 1)
        self.assertIn("10 + 20", entries[0].expression)
        self.assertEqual(entries[0].result, "30")


if __name__ == "__main__":
    unittest.main()
