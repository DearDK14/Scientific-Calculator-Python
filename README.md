# 🧮 Modern Scientific Calculator

A modern, professional desktop Scientific Calculator application built with **Python 3** and **CustomTkinter**. Designed as a portfolio-grade project, it pairs an Obsidian/Slate modern GUI with a robust, mathematically sound calculation engine isolated from the user interface.

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-CustomTkinter-blue)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Tests-54%2F54%20Passing-success)](test_calculator.py)

---

## 📖 1. Project Name
**Modern Scientific Calculator** (`ScientificCalculator`)

---

## 📝 2. Project Description
The **Modern Scientific Calculator** is an intuitive, reliable desktop application developed for students, engineers, and developers. Built strictly according to the **Separation of Concerns** principle, it combines an accessible, modern user experience (smooth dark/light themes, hover effects, native tooltips, dynamic font scaling) with a safe, sandbox-evaluated mathematical core (Python Abstract Syntax Tree parser, zero unrestricted `eval()`).

---

## ✨ 3. Features
- **🎨 Complete Theme System**: One-click toggle between Dark Mode and Light Mode with persistent configuration saved locally.
- **🛡️ Safe AST Math Evaluation**: Safe expression parsing using Python's `ast` module; preserves standard operator precedence (PEMDAS) without unsafe code execution.
- **🔬 20+ Scientific Operations**: Trigonometric, inverse trigonometric, hyperbolic, logarithms, exponential powers, roots, factorials, and constants.
- **📐 DEG & RAD Angle Modes**: Seamless switching between Degree and Radian angle units for trigonometric calculations.
- **🕒 Calculation History System**: Slide-out history drawer tracking previous calculations with timestamps, click-to-load restoring, and JSON file persistence.
- **💾 Full Memory Functions**: Complete memory registers (`MC`, `MR`, `M+`, `M-`, `MS`) with on-display `M` indicator badge and dynamic button state management.
- **📋 Clipboard Integration**: Dedicated `📋 Copy` button with animated `✓ Copied!` visual feedback, plus global `Ctrl+C` and sanitized `Ctrl+V` pasting.
- **⌨️ Complete Keyboard Support**: Identical behavior between physical keyboard inputs (top row and numpad) and on-screen buttons.
- **💡 Built-in Tooltips**: Informative hover tooltips for all scientific functions and memory keys without external package dependencies.
- **🛡️ Graceful Error Handling**: Never crashes on invalid expressions, division by zero, or domain errors; displays friendly error messages and recovers immediately upon typing.

---

## 🛠️ 4. Technologies Used
- **Python 3.8+**: Core programming language.
- **CustomTkinter**: Modern, high-DPI desktop GUI widgets with auto dark/light theme switching.
- **Tkinter**: Underlying window management, event bindings, and lightweight tooltip overlays.
- **Python Standard Library `math`**: High-precision mathematical functions without external math APIs.
- **Python Standard Library `ast`**: Safe Abstract Syntax Tree expression validation and evaluation.
- **Pillow (`PIL`)**: Window and desktop taskbar icon processing.

---

## 📸 5. Screenshots Placeholder

| Dark Mode | Light Mode |
| :---: | :---: |
| ![Dark Mode Mockup](assets/icons/calculator.png)<br>*(Dark modern obsidian interface with History drawer)* | ![Light Mode Mockup](assets/icons/calculator.png)<br>*(Clean, high-contrast daylight theme)* |

```
┌─────────────────────────────────────────────────────────────┐
│  [DEG]         SCIENTIFIC             [🕒 History]  [☀️]   │
├─────────────────────────────────────────────────────────────┤
│  DEG  M                                          [📋 Copy]  │
│                                                (25 + 15) × 2│
│                                                           80│
├─────────────────────────────────────────────────────────────┤
│   [MC]       [MR]       [M+]       [M-]       [MS]          │
├─────────────────────────────────────────────────────────────┤
│   [sin]      [cos]      [tan]                               │
│   [asin]     [acos]     [atan]                              │
│   [log]      [ln]       [√]                                 │
│   [x²]       [xʸ]       [π]                                 │
│   [e]        [!]        [%]                                 │
│   [exp]      [1/x]      [|x|]                               │
├─────────────────────────────────────────────────────────────┤
│   [ 7 ]      [ 8 ]      [ 9 ]      [ ÷ ]                    │
│   [ 4 ]      [ 5 ]      [ 6 ]      [ × ]                    │
│   [ 1 ]      [ 2 ]      [ 3 ]      [ − ]                    │
│   [ 0 ]      [ . ]      [ ± ]      [ + ]                    │
├─────────────────────────────────────────────────────────────┤
│   [ C ]      [ DEL ]    [ ( ]      [ ) ]      [ = ]         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📥 6. Installation Instructions

### Prerequisites
Make sure **Python 3.8 or higher** is installed on your computer.

### Step 1: Clone or Download the Repository
```bash
git clone https://github.com/DearDK14/Scientific-Calculator-Python.git
cd Scientific-Calculator-Python
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 7. How to Run

Launch the application directly with:
```bash
python main.py
```

To execute the full automated test suite:
```bash
python -m unittest test_calculator.py
```

---

## ⌨️ 8. Keyboard Shortcuts

The calculator captures keystrokes globally (`bind_all`) so button focus does not interfere with typing:

| Key(s) | Action | Description |
| :--- | :--- | :--- |
| `0` – `9` | Digits | Enters numbers (supports main keyboard & Numpad) |
| `.` | Decimal Point | Appends decimal separator |
| `+`, `-`, `*`, `/` | Arithmetic | Addition, Subtraction, Multiplication, Division |
| `^` | Power | Exponentiation operator ($x^y$) |
| `%` | Percentage | Calculates percentage ($x / 100$) |
| `!` | Factorial | Calculates factorial ($n!$) |
| `(` and `)` | Parentheses | Groups operations and establishes precedence |
| `Enter` / `=` | Equals | Evaluates expression safely |
| `Backspace` | Backspace | Deletes the trailing character |
| `Escape` / `c` | Clear | Clears current input line (`C`) |
| `p` / `P` | Constant $\pi$ | Inserts Archimedes' constant $\pi \approx 3.14159$ |
| `e` / `E` | Constant $e$ | Inserts Euler's number $e \approx 2.71828$ |
| `Ctrl + C` | Copy | Copies current result or expression to clipboard |
| `Ctrl + V` | Paste | Safely sanitizes and pastes expression from clipboard |
| `Ctrl + A` | Select All | Highlights active display readout |

---

## 🔬 9. Scientific Functions

All mathematical logic is located in [`scientific.py`](file:///v:/DK/2026-27/Calculator/scientific.py), leveraging Python's standard `math` library:

- **Trigonometric Functions**:
  - `sin(x)`: Sine of angle $x$.
  - `cos(x)`: Cosine of angle $x$.
  - `tan(x)`: Tangent of angle $x$ (safely flags undefined at $90^\circ$).
- **Inverse Trigonometric Functions**:
  - `asin(x)`: Arcsine (valid for $-1 \le x \le 1$).
  - `acos(x)`: Arccosine (valid for $-1 \le x \le 1$).
  - `atan(x)`: Arctangent (valid for all real numbers).
- **Logarithms & Exponentials**:
  - `log(x)`: Common logarithm (base 10, requires $x > 0$).
  - `ln(x)`: Natural logarithm (base $e$, requires $x > 0$).
  - `exp(x)`: Exponential function ($e^x$).
- **Advanced Algebra**:
  - `x²`: Square of a number.
  - `xʸ`: Number $x$ raised to arbitrary power $y$.
  - `√`: Square root ($\sqrt{x}$, requires $x \ge 0$).
  - `1/x`: Multiplicative inverse / reciprocal ($x \ne 0$).
  - `x!`: Factorial ($n \ge 0$, integer-only, overflow guarded up to 170).
  - `|x|`: Absolute value of $x$.
  - `%`: Converts operand to percentage ($x / 100$).
  - `±`: Toggles sign between positive and negative.
- **Mathematical Constants**:
  - $\pi \approx 3.1415926535...$
  - $e \approx 2.7182818284...$

---

## 📐 10. DEG/RAD Mode
- **Degree Mode (`DEG`)**: Standard setting for geometry and navigation ($90^\circ = \pi/2$ radians).
  - Example: `sin(30)` in DEG returns `0.5`.
- **Radian Mode (`RAD`)**: Essential for calculus and advanced trigonometry.
  - Example: `sin(pi / 6)` in RAD returns `0.5`.
- **Switching Modes**: Click the **`DEG`/`RAD`** button in the top bar to toggle instantly. The status badge on the display updates in real time.

---

## 🕒 11. History System
- **Interactive Drawer**: Slide-out history panel on the right side of the window, toggled via **`🕒 History`**.
- **Formatted Cards**: Displays each calculation with formatted expression, bold result, and local timestamp (e.g. `25 × 4 = 100` at `14:32:05`).
- **Click to Restore**: Clicking any historical card restores both its expression and result directly back into the calculator display.
- **Persistence & Limits**: History automatically loads on application start from `calculator_history.json` and is capped at 50 records.
- **Clear Action**: A dedicated **"Clear History"** button empties stored calculations from both memory and disk.

---

## 💾 12. Memory Functions
A dedicated 5-button memory toolbar is positioned directly below the display card:

| Button | Function | Description |
| :--- | :--- | :--- |
| `MC` | Memory Clear | Resets stored memory value to `0` and turns off `M` indicator |
| `MR` | Memory Recall | Recalls the stored memory number into the current calculation display |
| `M+` | Memory Add | Adds the current result or input value to memory |
| `M-` | Memory Subtract | Subtracts the current result or input value from memory |
| `MS` | Memory Store | Overwrites memory with the active value and illuminates the `M` indicator |

- **Indicator**: A distinct **`M`** badge illuminates in the display card header whenever memory contains a value.
- **State Protection**: When memory is empty, `MC` and `MR` are automatically disabled and dimmed, mirroring professional desktop calculator standards.

---

## 🛡️ Error Handling & Recovery
The calculator never crashes on invalid user input:

| Error Case | Displayed Message | Recovery Behavior |
| :--- | :--- | :--- |
| Division by zero (`10 / 0`) | `"Cannot divide by zero"` | Typing any number or operator begins fresh calculation |
| Mismatched syntax (`5 + * 2`) | `"Invalid expression"` | Typing or clicking clears error automatically |
| Negative square root (`√(-4)`) | `"Math domain error"` | User can continue without pressing Clear |
| Negative / float factorial (`(-3)!` / `3.5!`) | `"Math domain error"` | Clean friendly message |
| Logarithm of zero (`log(0)`) | `"Math domain error"` | Domain guarded |
| Arcsin out of range (`asin(2)`) | `"Math domain error"` | Domain guarded |
| Numerical overflow (`10 ^ 500`) | `"Overflow: Result too large"` | Overflow protection prevents Python float crash |
| Multiple decimal points (`5.5.5`) | Handled cleanly / prevented | Never crashes the parser |
| Unclosed parentheses (`((2 + 3)`) | Auto-balanced to `5` | Evaluates gracefully |

---

## 📁 13. Project Structure

```
ScientificCalculator/
│
├── main.py                   # CustomTkinter GUI, event dispatching & tooltips
├── calculator.py             # AST evaluator, expression sanitizer & memory state
├── scientific.py             # Pure mathematical scientific engine (Python math module)
├── history.py                # Calculation history tracker & JSON persistence
├── theme.py                  # Dark/Light palettes, fonts, ThemeManager & CTkToolTip
├── test_calculator.py        # 54 comprehensive unit tests (100% passing)
├── requirements.txt          # Python dependencies (customtkinter, pillow)
├── README.md                 # Complete documentation guide
├── LICENSE                   # Open-source MIT License
│
├── calculator_history.json   # Local auto-saved calculation history (gitignored)
├── calculator_settings.json  # Local auto-saved user theme preferences (gitignored)
│
└── assets/
    └── icons/
        ├── calculator.ico    # Desktop window and title bar icon
        └── calculator.png    # High-resolution application icon
```

---

## 🔮 14. Future Improvements
- [ ] **Graphing Mode**: Plot 2D mathematical functions ($y = f(x)$) on an interactive canvas.
- [ ] **Unit & Currency Converter**: Length, mass, temperature, and currency conversion tab.
- [ ] **Matrix & Vector Algebra**: Support for determinant, dot product, and matrix multiplication.
- [ ] **Programmer Base Mode**: Binary, Octal, Decimal, and Hexadecimal bitwise operations (AND, OR, XOR, NOT).
- [ ] **Multi-variable Equation Solver**: Numerical root finding using Newton-Raphson method.

---

## 👤 15. Author Section
Developed with ❤️ by **Dinesh Kumar** ([DearDK14](https://github.com/DearDK14))

- **GitHub**: [@DearDK14](https://github.com/DearDK14)
- **Repository**: [Scientific-Calculator-Python](https://github.com/DearDK14/Scientific-Calculator-Python)
- **Feedback & Issues**: Contributions and feature requests are welcome! Feel free to open an issue or pull request on the repository.
