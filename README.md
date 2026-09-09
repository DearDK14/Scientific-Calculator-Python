# 🧮 Modern Scientific Calculator (Python & CustomTkinter)

A modern, elegant desktop Scientific Calculator built using **Python 3** and **CustomTkinter**. The application strictly isolates calculation logic from GUI presentation, making it both powerful for everyday use and straightforward for beginners to study and extend.

---

## ✨ Features

- **🎨 Modern Dark & Light Themes**: Smooth one-click toggle between sleek dark mode and crisp light mode.
- **🔄 Dual Layout Modes**:
  - **Standard Mode**: Compact, streamlined 4x5 keypad for everyday arithmetic.
  - **Scientific Mode**: Expanded panel offering 20+ scientific functions.
- **📐 Angle Modes**: Switch effortlessly between **Degrees (DEG)** and **Radians (RAD)** for all trigonometric operations.
- **🛡️ Safe AST Math Parser**: Safe evaluation using Python's built-in `ast` module—preserves standard mathematical operator precedence (PEMDAS) without relying on dangerous `eval()`.
- **🕒 Interactive History Drawer**:
  - Slide-out panel tracking recent calculations with timestamps.
  - Click any historical entry to restore its formula and result directly back to the display.
  - Local JSON persistence across application sessions.
- **💾 Memory Registers**: Full memory management (`MC`, `MR`, `M+`, `M-`, `MS`) with on-screen indicator.
- **⌨️ Keyboard Support**: Complete keyboard bindings for digits, operators, parentheses, enter, backspace, and clear.
- **📦 Zero External Math Dependencies**: Built strictly using Python's standard library `math` module.

---

## 📁 Project Structure

```
ScientificCalculator/
│
├── main.py              # CustomTkinter GUI layout, event handling & user interaction
├── calculator.py        # Core calculation engine, expression sanitizer & AST evaluator
├── scientific.py        # Pure scientific math functions using Python's math module
├── history.py           # Calculation history tracking & local JSON persistence
├── theme.py             # Themes, dynamic color palettes, fonts & appearance manager
├── test_calculator.py   # Unit test suite verifying math operations & engine state
├── requirements.txt     # Dependencies (customtkinter, pillow)
├── README.md            # Project documentation & beginner guide
│
└── assets/
    └── icons/           # Application icons (.ico and .png)
```

---

## 🧩 Architecture: How the Code Works

This project is built around the principle of **Separation of Concerns**:

1. **`scientific.py` (Pure Math)**:
   Contains standalone scientific functions (`sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `ln`, `log10`, `sqrt`, `factorial`, `power`, etc.) powered entirely by Python's built-in `math` library. It has no dependencies on the user interface.

2. **`calculator.py` (Engine & State)**:
   Maintains the calculator state (current input line, previous formula, angle mode, memory). It uses `SafeMathEvaluator` to parse expressions into an Abstract Syntax Tree (AST), ensuring mathematical operator precedence and rejecting unsafe code execution.

3. **`history.py` (History Tracking)**:
   Manages history records (`HistoryEntry`) and persists them to `calculator_history.json`.

4. **`theme.py` (Styling & Design)**:
   Centralizes color definitions for buttons, backgrounds, and fonts for both Dark and Light modes.

5. **`main.py` (GUI)**:
   Renders the window and widgets using CustomTkinter. When buttons are clicked or keys are pressed, `main.py` simply delegates the operation to `CalculatorEngine` and refreshes the screen.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/DearDK14/Scientific-Calculator-Python.git
cd Scientific-Calculator-Python
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Calculator
```bash
python main.py
```

---

## 🧪 Running Unit Tests

To run the automated test suite and verify calculation correctness:

```bash
python -m unittest test_calculator.py
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `0` - `9` | Enter numbers |
| `.` | Decimal point |
| `+`, `-`, `*`, `/` | Basic arithmetic operators |
| `^` | Power / Exponentiation |
| `(` and `)` | Parentheses |
| `Enter` or `=` | Calculate result |
| `Backspace` | Delete last character |
| `Delete` | Clear current input (`C`) |
| `Escape` | All Clear (`AC`) |
| `p` / `P` | Insert constant $\pi$ |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
