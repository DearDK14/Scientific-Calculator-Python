"""
placeholder_view.py
===================
Polished placeholder view for upcoming calculator and converter modes.
Provides an extensible template ready for future calculation engine integration.
"""

from typing import Any
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts


class PlaceholderView(BaseModeView):
    """
    Extensible template view for upcoming modes:
    - Graphing, Programmer, Date Calculation
    - Currency, Volume, Length, Weight and Mass, Temperature, Energy,
      Area, Speed, Time, Power, Data, Pressure, Angle.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app: Any,
        mode_id: str,
        title: str,
        category: str,
        icon: str,
        description: str,
        **kwargs
    ):
        super().__init__(parent, app, **kwargs)
        self._mode_id = mode_id
        self._title = title
        self._category = category
        self._icon = icon
        self._description = description

        self._build_ui()

    def get_title(self) -> str:
        return self._title

    def get_mode_id(self) -> str:
        return self._mode_id

    def handles_keyboard(self) -> bool:
        return False

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Center Card
        card = ctk.CTkFrame(
            self,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=16,
        )
        card.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(5, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=self._icon,
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=48),
        )
        icon_label.grid(row=0, column=0, pady=(40, 8))

        # Category Pill
        pill = ctk.CTkLabel(
            card,
            text=self._category.upper(),
            font=Fonts.label_badge(),
            text_color=Theme.TEXT_ACCENT,
            fg_color=Theme.PANEL_BG,
            corner_radius=8,
            padx=10,
            pady=4,
        )
        pill.grid(row=1, column=0, pady=(0, 10))

        # Title
        title_lbl = ctk.CTkLabel(
            card,
            text=self._title,
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=24, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title_lbl.grid(row=2, column=0, pady=(0, 8))

        # Description
        desc_lbl = ctk.CTkLabel(
            card,
            text=self._description,
            font=Fonts.history_expr(),
            text_color=Theme.TEXT_SECONDARY,
            wraplength=450,
            justify="center",
        )
        desc_lbl.grid(row=3, column=0, padx=20, pady=(0, 24))

        # Status Tag / Roadmap
        info_box = ctk.CTkFrame(
            card,
            fg_color=Theme.PANEL_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        info_box.grid(row=4, column=0, padx=32, pady=(0, 30), sticky="ew")
        info_box.grid_columnconfigure(0, weight=1)

        info_header = ctk.CTkLabel(
            info_box,
            text="Modular Architecture Ready",
            font=Fonts.tab_title(),
            text_color=Theme.TEXT_SUCCESS,
            anchor="w",
        )
        info_header.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        info_body = ctk.CTkLabel(
            info_box,
            text=(
                f"The '{self._title}' view is registered within the application shell. "
                "Its calculation engine and UI widgets will be plugged in as modular sub-components "
                "implementing BaseModeView."
            ),
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_SECONDARY,
            wraplength=400,
            justify="left",
            anchor="w",
        )
        info_body.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")
