"""
sidebar.py
==========
Collapsible left navigation sidebar component for the Modern Calculator Application Shell.
Contains categorized navigation:
- Calculator: Standard, Scientific, Graphing, Programmer, Date Calculation
- Converter: Currency, Volume, Length, Weight and Mass, Temperature, Energy,
             Area, Speed, Time, Power, Data, Pressure, Angle
- Bottom: Settings
"""

from typing import Callable, Dict, List, Tuple
import customtkinter as ctk

from theme import Theme, Fonts, CTkToolTip


class SidebarNavigation(ctk.CTkFrame):
    """
    Collapsible left sidebar providing categorized navigation.
    Dispatches mode changes to the application shell without opening new windows.
    """

    # Category definitions: (category_name, [(mode_id, display_label, icon, description)])
    NAV_SECTIONS: List[Tuple[str, List[Tuple[str, str, str, str]]]] = [
        (
            "Calculator",
            [
                ("standard", "Standard", "🧮", "Basic everyday arithmetic calculations"),
                ("scientific", "Scientific", "🔬", "Trigonometric, logarithmic, and advanced math operations"),
                ("graphing", "Graphing", "📈", "Interactive 2D mathematical function plots"),
                ("programmer", "Programmer", "💻", "Binary, octal, decimal, and hexadecimal bitwise logic"),
                ("date_calc", "Date Calculation", "📅", "Difference between dates and date addition"),
            ],
        ),
        (
            "Converter",
            [
                ("currency", "Currency", "💱", "Real-time exchange rates and currency conversion"),
                ("volume", "Volume", "🧪", "Liters, gallons, fluid ounces, milliliters, and cups"),
                ("length", "Length", "📏", "Inches, feet, meters, centimeters, miles, and kilometers"),
                ("weight", "Weight and Mass", "⚖️", "Pounds, kilograms, ounces, grams, and stone"),
                ("temperature", "Temperature", "🌡️", "Celsius, Fahrenheit, and Kelvin conversions"),
                ("energy", "Energy", "⚡", "Joules, calories, electron-volts, and kilowatt-hours"),
                ("area", "Area", "📐", "Square meters, square feet, acres, and hectares"),
                ("speed", "Speed", "🚗", "Miles per hour, kilometers per hour, knots, and m/s"),
                ("time", "Time", "⏱️", "Milliseconds, seconds, minutes, hours, days, and weeks"),
                ("power", "Power", "💡", "Watts, kilowatts, horsepower, and foot-pounds/min"),
                ("data", "Data", "💾", "Bits, bytes, kilobytes, megabytes, gigabytes, and terabytes"),
                ("pressure", "Pressure", "🔘", "Atmospheres, bars, pascals, psi, and torr"),
                ("angle", "Angle", "🧭", "Degrees, radians, and gradians conversions"),
            ],
        ),
    ]

    BOTTOM_SECTION: List[Tuple[str, str, str, str]] = [
        ("settings", "Settings", "⚙️", "Application appearance, angle defaults, and history settings"),
    ]

    def __init__(
        self,
        parent: ctk.CTkFrame,
        on_mode_select: Callable[[str], None],
        initial_mode: str = "standard",
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=Theme.SIDEBAR_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=0,
            width=230,
            **kwargs,
        )
        self.on_mode_select = on_mode_select
        self.active_mode = initial_mode
        self.is_collapsed = False
        self.button_map: Dict[str, ctk.CTkButton] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Scrollable area
        self.grid_rowconfigure(1, weight=0)  # Pinned bottom (Settings)

        # 1. Scrollable Navigation Body
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=(10, 6))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        row_idx = 0
        for section_title, items in self.NAV_SECTIONS:
            # Section Header
            sec_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text=section_title.upper(),
                font=Fonts.sidebar_header(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            sec_lbl.grid(row=row_idx, column=0, padx=10, pady=(12 if row_idx > 0 else 4, 4), sticky="w")
            row_idx += 1

            # Navigation Items
            for mode_id, label, icon, tip in items:
                btn = self._create_nav_button(
                    parent=self.scroll_frame,
                    mode_id=mode_id,
                    label=f"{icon}  {label}",
                    tooltip=tip,
                )
                btn.grid(row=row_idx, column=0, sticky="ew", pady=1)
                self.button_map[mode_id] = btn
                row_idx += 1

        # 2. Bottom Divider & Pinned Settings
        bottom_container = ctk.CTkFrame(self, fg_color="transparent")
        bottom_container.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 12))
        bottom_container.grid_columnconfigure(0, weight=1)

        divider = ctk.CTkFrame(bottom_container, fg_color=Theme.DIVIDER_COLOR, height=1)
        divider.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        for mode_id, label, icon, tip in self.BOTTOM_SECTION:
            btn = self._create_nav_button(
                parent=bottom_container,
                mode_id=mode_id,
                label=f"{icon}  {label}",
                tooltip=tip,
            )
            btn.grid(row=1, column=0, sticky="ew")
            self.button_map[mode_id] = btn

        # Highlight initially active mode
        self.set_active_mode(self.active_mode)

    def _create_nav_button(
        self, parent: ctk.CTkFrame, mode_id: str, label: str, tooltip: str
    ) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            parent,
            text=label,
            font=Fonts.sidebar_item(),
            command=lambda m=mode_id: self._handle_click(m),
            **Theme.BTN_SIDEBAR,
        )
        CTkToolTip(btn, tooltip)
        return btn

    def _handle_click(self, mode_id: str) -> None:
        self.set_active_mode(mode_id)
        self.on_mode_select(mode_id)

    def set_active_mode(self, mode_id: str) -> None:
        """Visually marks the given mode as selected."""
        self.active_mode = mode_id
        for m_id, btn in self.button_map.items():
            if m_id == mode_id:
                btn.configure(
                    fg_color=Theme.BTN_SIDEBAR_ACTIVE["fg_color"],
                    hover_color=Theme.BTN_SIDEBAR_ACTIVE["hover_color"],
                    text_color=Theme.BTN_SIDEBAR_ACTIVE["text_color"],
                )
            else:
                btn.configure(
                    fg_color=Theme.BTN_SIDEBAR["fg_color"],
                    hover_color=Theme.BTN_SIDEBAR["hover_color"],
                    text_color=Theme.BTN_SIDEBAR["text_color"],
                )

    def toggle(self) -> bool:
        """
        Toggles sidebar between collapsed (hidden) and expanded.
        Returns the new collapsed state (True if hidden, False if visible).
        """
        if self.winfo_viewable():
            self.grid_remove()
            self.is_collapsed = True
        else:
            self.grid()
            self.is_collapsed = False
        return self.is_collapsed

    def collapse(self) -> None:
        """Hides the sidebar."""
        self.grid_remove()
        self.is_collapsed = True

    def expand(self) -> None:
        """Shows the sidebar."""
        self.grid()
        self.is_collapsed = False
