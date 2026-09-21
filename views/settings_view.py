"""
settings_view.py
================
Settings mode view for user preferences, appearance themes, and storage management.
"""

from typing import Any
import customtkinter as ctk

from views.base_view import BaseModeView
from theme import Theme, Fonts, CTkToolTip


class SettingsView(BaseModeView):
    """
    Settings view for configuring application appearance, calculator defaults,
    and history storage.
    """

    def __init__(self, parent: ctk.CTkFrame, app: Any, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build_ui()

    def get_title(self) -> str:
        return "Settings"

    def get_mode_id(self) -> str:
        return "settings"

    def handles_keyboard(self) -> bool:
        return False

    def on_activate(self) -> None:
        self._refresh_values()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        scroll_container.grid_columnconfigure(0, weight=1)

        # 1. Appearance Section
        self._build_card(
            scroll_container,
            title="Appearance Theme",
            description="Select whether the calculator uses Dark Mode or Light Mode. Choice persists across restarts.",
            row=0,
            content_builder=self._build_theme_controls,
        )

        # 2. Angle Mode Section
        self._build_card(
            scroll_container,
            title="Trigonometric Angle Unit",
            description="Choose default angle unit (Degrees or Radians) for trigonometric calculations.",
            row=1,
            content_builder=self._build_angle_controls,
        )

        # 3. History Management Section
        self._build_card(
            scroll_container,
            title="Calculation History Storage",
            description="Manage saved calculations stored in calculator_history.json.",
            row=2,
            content_builder=self._build_history_controls,
        )

        # 4. About Section
        self._build_card(
            scroll_container,
            title="About Modern Scientific Calculator",
            description="Version 1.0.0 • Python 3 & CustomTkinter • Open Source MIT",
            row=3,
            content_builder=self._build_about_info,
        )

    def _build_card(self, parent, title: str, description: str, row: int, content_builder) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.CARD_BG,
            border_color=Theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12,
        )
        card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            card,
            text=title,
            font=Fonts.history_title(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        header.grid(row=0, column=0, padx=16, pady=(12, 2), sticky="w")

        desc = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
            wraplength=480,
            justify="left",
        )
        desc.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        body_frame = ctk.CTkFrame(card, fg_color="transparent")
        body_frame.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="ew")
        content_builder(body_frame)

    def _build_theme_controls(self, parent: ctk.CTkFrame) -> None:
        current_mode = self.app.theme_mgr.current_mode.capitalize()
        self.theme_segment = ctk.CTkSegmentedButton(
            parent,
            values=["Dark", "Light"],
            command=self._on_theme_changed,
            font=Fonts.tab_title(),
        )
        self.theme_segment.set(current_mode)
        self.theme_segment.pack(side="left")

    def _build_angle_controls(self, parent: ctk.CTkFrame) -> None:
        current_angle = self.app.engine.angle_mode
        self.angle_segment = ctk.CTkSegmentedButton(
            parent,
            values=["DEG", "RAD"],
            command=self._on_angle_changed,
            font=Fonts.tab_title(),
        )
        self.angle_segment.set(current_angle)
        self.angle_segment.pack(side="left")

    def _build_history_controls(self, parent: ctk.CTkFrame) -> None:
        count = len(self.app.history_mgr.get_all())
        self.history_info_lbl = ctk.CTkLabel(
            parent,
            text=f"Currently storing {count} calculations (Max limit: {self.app.history_mgr.max_entries}).",
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.history_info_lbl.pack(side="left", padx=(0, 14))

        clear_btn = ctk.CTkButton(
            parent,
            text="🗑️ Clear All History",
            command=self._on_clear_history,
            font=Fonts.label_badge(),
            **Theme.BTN_ACTION,
            height=28,
        )
        clear_btn.pack(side="left")

    def _build_about_info(self, parent: ctk.CTkFrame) -> None:
        lbl = ctk.CTkLabel(
            parent,
            text="Developed by Dinesh Kumar (@DearDK14)\nInspired by modern desktop calculators with zero proprietary assets.",
            font=ctk.CTkFont(family=Fonts.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_SECONDARY,
            justify="left",
            anchor="w",
        )
        lbl.pack(side="left")

    def _on_theme_changed(self, value: str) -> None:
        mode = value.lower()
        self.app.theme_mgr.set_mode(mode)
        self.app._update_theme_icon()

    def _on_angle_changed(self, value: str) -> None:
        self.app.engine.set_angle_mode(value)
        if hasattr(self.app, "current_view") and hasattr(self.app.current_view, "_update_display"):
            self.app.current_view._update_display()

    def _on_clear_history(self) -> None:
        self.app.history_mgr.clear()
        self._refresh_values()
        if hasattr(self.app, "history_memory_panel"):
            self.app.history_memory_panel.refresh()

    def _refresh_values(self) -> None:
        if hasattr(self, "theme_segment"):
            self.theme_segment.set(self.app.theme_mgr.current_mode.capitalize())
        if hasattr(self, "angle_segment"):
            self.angle_segment.set(self.app.engine.angle_mode)
        if hasattr(self, "history_info_lbl"):
            count = len(self.app.history_mgr.get_all())
            self.history_info_lbl.configure(
                text=f"Currently storing {count} calculations (Max limit: {self.app.history_mgr.max_entries})."
            )
